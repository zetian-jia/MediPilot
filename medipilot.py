import os
import time
import base64
import json
import pyautogui
import mss
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI

# =================================================================
# MediPilot: 医疗场景自动化 AI Agent
# 架构：感知 (Perception) -> 认知 (Reasoning) -> 执行 (Execution)
# =================================================================

# --- 1. 配置与知识库 (Configuration & Knowledge Base) ---

# 建议使用环境变量存储 API Key
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"
client = OpenAI()

class MedicalTranslator:
    """
    医疗术语映射表，解决化验单与系统描述不一致问题。
    """
    MAPPING = {
        "WBC": "白细胞计数",
        "RBC": "红细胞计数",
        "Hgb": "血红蛋白",
        "PLT": "血小板计数",
        "NEUT%": "中性粒细胞百分比",
        "LYMPH%": "淋巴细胞百分比",
        "HCT": "红细胞压积",
        "MCV": "平均红细胞体积"
    }

    @classmethod
    def translate(cls, term):
        return cls.MAPPING.get(term.upper(), term)

# --- 2. 感知层 (Layer 1: Perception - The Eye) ---

class Perception:
    def __init__(self):
        self.sct = mss.mss()

    def capture(self):
        """高频低延迟截屏"""
        monitor = self.sct.monitors[1]
        sct_img = self.sct.grab(monitor)
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    def privacy_filter(self, image):
        """
        医疗特有：隐私过滤器。
        在发送给云端 LLM 前，本地检测并模糊化敏感信息 (PII)。
        """
        cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 模拟：本地运行轻量级检测模型（如 YOLO/PaddleOCR）
        # 这里手动指定一个区域（如顶部状态栏/病人信息栏）进行高斯模糊
        height, width, _ = cv_img.shape
        # 假设病人姓名/ID 位于左上角区域 (0,0) 到 (400, 150)
        roi = cv_img[0:150, 0:400]
        blurred_roi = cv2.GaussianBlur(roi, (51, 51), 0)
        cv_img[0:150, 0:400] = blurred_roi
        
        return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

    def apply_som_overlay(self, image, grid_size=80):
        """
        视觉锚点 (Visual Grounding)：Grid/Set-of-Mark Overlay。
        将像素坐标转化为 LLM 可理解的区域编码。
        """
        draw = ImageDraw.Draw(image)
        w, h = image.size
        
        # 绘制网格与标签
        for x in range(0, w, grid_size):
            draw.line([(x, 0), (x, h)], fill=(255, 0, 0, 128), width=1)
            for y in range(0, h, grid_size):
                draw.line([(0, y), (w, y)], fill=(255, 0, 0, 128), width=1)
                
                # 编码示例：A1, B2...
                col = chr(65 + (x // grid_size) % 26)
                row = y // grid_size
                label = f"{col}{row}"
                draw.text((x + 2, y + 2), label, fill="red")
        
        return image

# --- 3. 认知层 (Layer 2: Cognition - The Brain) ---

class Brain:
    def __init__(self, model="gpt-4o"):
        self.model = model

    def _encode_image(self, image):
        import io
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def extract_data_prompt(self):
        """提示词 A：用于读取化验单截图"""
        return """
        # Context
        你是一个专业的医疗数据提取助手。你面前是一张覆盖了坐标网格的化验单截图。
        
        # Goal
        提取以下结构化指标（如有）：
        1. WBC (白细胞), 2. RBC (红细胞), 3. Hgb (血红蛋白), 4. PLT (血小板)。
        
        # Output Format (JSON)
        {
            "findings": [{"metric": "WBC", "value": "x.x", "unit": "10^9/L"}],
            "confidence": 0.95
        }
        """

    def ui_operation_prompt(self, task_state):
        """提示词 B：用于 UI 自动化控制"""
        return f"""
        # Context
        你是一个医疗自动化 Agent 'MediPilot'。当前任务状态: {task_state}。
        
        # Visual Grounding
        屏幕已标记红色网格。坐标格式如 [x, y]（像素）。
        
        # Constraints
        - 仅输出下一步动作。
        - 确保操作精准，避免点击到无关区域。
        
        # Output Format (JSON)
        {{
            "thought": "分析当前 UI 状态...",
            "action": "click" | "type" | "scroll" | "wait" | "finish",
            "coordinate": [x, y],
            "text": "输入内容",
            "reasoning": "执行此步的临床/操作依据"
        }}
        """

    def call_vision(self, image, prompt):
        """调用 GPT-4o / Claude 3.5 API"""
        b64_img = self._encode_image(image)
        
        response = client.chat.completions.create(
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

# --- 4. 执行层 (Layer 3: Execution - The Hand) ---

class Executor:
    def __init__(self):
        # Safe Guard: 动作限速
        pyautogui.PAUSE = 0.8
        # Safe Guard: 紧急停止（鼠标甩至屏幕四角）
        pyautogui.FAILSAFE = True

    def execute(self, plan):
        action = plan.get("action")
        coord = plan.get("coordinate")
        text = plan.get("text")

        print(f"执行动作: {action.upper()} | 依据: {plan.get('reasoning')}")

        if action == "click":
            pyautogui.moveTo(coord[0], coord[1], duration=0.5)
            pyautogui.click()
        elif action == "type":
            pyautogui.click(coord[0], coord[1])
            pyautogui.write(text, interval=0.1)
        elif action == "scroll":
            pyautogui.scroll(-500)
        elif action == "wait":
            time.sleep(2)
        elif action == "finish":
            return True
        return False

# --- 5. 任务编排器 (Task Planner & Main) ---

class MediPilot:
    def __init__(self):
        self.perception = Perception()
        self.brain = Brain()
        self.executor = Executor()
        self.extracted_data = None

    def run(self):
        print("--- MediPilot 启动 (医疗自动化 Agent) ---")
        
        # 步骤 1: 观察并提取化验单数据
        print("步骤 1: 正在扫描化验单数据...")
        raw_img = self.perception.capture()
        safe_img = self.perception.privacy_filter(raw_img)
        som_img = self.perception.apply_som_overlay(safe_img)
        
        self.extracted_data = self.brain.call_vision(som_img, self.brain.extract_data_prompt())
        print(f"成功提取数据: {json.dumps(self.extracted_data, indent=2, ensure_ascii=False)}")

        # 步骤 2: 将数据录入 EMR 系统
        print("\n步骤 2: 开始执行 UI 录入流程...")
        task_context = f"已提取数据: {self.extracted_data}。现在请在 EMR 系统中找到对应输入框并填入。"
        
        while True:
            # 实时感知
            current_screen = self.perception.capture()
            # 隐私过滤（防止在操作过程中泄露其他病人信息）
            safe_screen = self.perception.privacy_filter(current_screen)
            # 添加网格辅助定位
            visual_grounding_screen = self.perception.apply_som_overlay(safe_screen)
            
            # 推理下一步动作
            plan = self.brain.call_vision(visual_grounding_screen, self.brain.ui_operation_prompt(task_context))
            
            # 执行
            if self.executor.execute(plan):
                print("--- 任务圆满完成 ---")
                break
            
            # 状态更新
            task_context += f"\n已完成上一步: {plan.get('thought')}"
            time.sleep(1)

if __name__ == "__main__":
    # 使用示例
    # pilot = MediPilot()
    # pilot.run()
    print("MediPilot 架构代码已生成。")
    print("关键模块：")
    print("- 感知层: 支持隐私过滤与 SoM 视觉网格")
    print("- 认知层: 具备数据提取与 UI 操作双提示词策略")
    print("- 执行层: 内置 Safe Guard 安全防护机制")
