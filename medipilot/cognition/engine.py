import base64
import json
import io
from openai import OpenAI
from configs.settings import config

class Brain:
    def __init__(self, model=config.VISION_MODEL):
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
        self.model = model

    def _encode_image(self, image):
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def call_vision(self, image, prompt):
        b64_img = self._encode_image(image)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个严谨的医疗自动化助手。"},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                    ],
                }
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

class Prompts:
    @staticmethod
    def extraction():
        """
        场景：数据提取 Prompt (读取化验单)
        Context: 你获得了一张化验单的截图。
        Goal: 提取结构化数据，准备录入。
        """
        return """
        # Context
        你是一个严谨的医疗化验单分析助手。你面前是一张覆盖了视觉锚点网格的化验单截图。
        
        # Goal
        从截图中提取以下目标指标的结构化数据，用于后续的自动化打字录入。
        
        # Target Metrics Mapping
        1. WBC (白细胞计数): 寻找单位为 10^9/L 的数值
        2. RBC (红细胞计数): 寻找单位为 10^12/L 的数值
        3. Hgb (血红蛋白): 寻找单位为 g/L 的数值
        4. PLT (血小板计数): 寻找单位为 10^9/L 的数值
        
        # Output Format (Strict JSON)
        {
            "findings": [
                {
                    "metric": "WBC",
                    "value": "7.2",
                    "unit": "10^9/L",
                    "target_field_hint": "白细胞"
                }
            ],
            "total_extracted": 4,
            "scan_quality": "High"
        }
        
        # Constraints
        - 仅提取数值，不要带单位。
        - 如果数值模糊无法确认，请标记信心度。
        - 确保 metric 名称与映射表严格一致，以便自动录入系统识别。
        """
    
    @staticmethod
    def operation(task_state):
        """
        场景：UI 自动化录入 Prompt
        Context: 已经获得结构化数据，正在面对电子病历 (EMR) 录入系统。
        """
        return f"""
        # Context
        你是一个医疗自动化 Agent 'MediPilot'。
        当前持有的结构化数据: {task_state}
        
        # Goal
        根据屏幕截图中的红色网格标签（如 A1, B2），执行自动打字录入任务。
        
        # Execution Steps
        1. 在屏幕上寻找目标指标对应的输入框。
        2. 计算其在视觉网格中的中心像素坐标。
        3. 输出 click 动作以聚焦，随后输出 type 动作进行打字录入。
        
        # Output Format (JSON)
        {{
            "thought": "我看到了白细胞输入框在 B4 位置...",
            "action": "click" | "type" | "finish",
            "coordinate": [x, y],
            "text": "录入的数值",
            "reasoning": "点击并录入 WBC 数据"
        }}
        """
