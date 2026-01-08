import base64
import json
import io
from typing import Dict, Any, Optional
from PIL import Image
from openai import OpenAI
from openai import APIError, RateLimitError, APIConnectionError
from configs.settings import config
from medipilot.utils.logger import audit_logger

class CognitionError(Exception):
    """认知层异常"""
    pass

class Brain:
    """
    认知层：决策大脑
    负责处理多模态输入，生成结构化提取结果或 UI 操作指令。
    
    Attributes:
        client: OpenAI客户端实例
        model: 使用的模型名称
    """
    
    def __init__(self, model: Optional[str] = None) -> None:
        """
        初始化认知引擎
        
        Args:
            model: 模型名称，默认使用配置中的VISION_MODEL
            
        Raises:
            CognitionError: 初始化失败时抛出
        """
        try:
            self.client = OpenAI(
                api_key=config.OPENAI_API_KEY,
                base_url=config.OPENAI_BASE_URL
            )
            self.model = model or config.VISION_MODEL
            audit_logger.info(f"认知引擎启动，当前模型: {self.model}")
        except Exception as e:
            audit_logger.critical(f"认知引擎初始化失败: {e}")
            raise CognitionError(f"无法初始化AI引擎: {e}")

    def _encode_image(self, image: Image.Image) -> str:
        """
        将 PIL 图像转换为 base64 编码，用于 API 传输
        
        Args:
            image: PIL图像对象
            
        Returns:
            str: Base64编码的图像字符串
            
        Raises:
            CognitionError: 图像编码失败时抛出
        """
        try:
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            encoded = base64.b64encode(buffered.getvalue()).decode('utf-8')
            audit_logger.debug(f"图像编码完成，大小: {len(encoded)} 字符")
            return encoded
        except Exception as e:
            audit_logger.error(f"图像编码失败: {e}")
            raise CognitionError(f"图像编码错误: {e}")

    def call_vision(self, image: Image.Image, prompt: str) -> Dict[str, Any]:
        """
        调用视觉大模型进行分析
        
        Args:
            image: 经过脱敏和 SoM 处理的截图
            prompt: 系统或用户提示词
            
        Returns:
            dict: 模型生成的 JSON 结果
            
        Raises:
            CognitionError: API调用失败时抛出（严重错误）
        """
        try:
            b64_img = self._encode_image(image)
            audit_logger.info("正在发送视觉请求至大模型...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个极其严谨的医疗自动化助手。你的每一个操作都关系到医疗质量，必须严格遵守指令。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                        ],
                    }
                ],
                response_format={"type": "json_object"},
                timeout=30.0  # 30秒超时
            )
            
            result = json.loads(response.choices[0].message.content)
            audit_logger.info(f"模型思考结果: {result.get('thought', '无')[:100]}...")
            
            # 验证返回结果包含必要字段
            if "action" not in result and "findings" not in result:
                audit_logger.warning("模型返回结果缺少关键字段，可能格式不正确")
            
            return result
            
        except RateLimitError as e:
            audit_logger.error(f"API调用超出限额: {e}")
            return {
                "action": "error",
                "reason": "API调用频率超限，请稍后重试",
                "error_type": "rate_limit"
            }
        except APIConnectionError as e:
            audit_logger.error(f"API连接失败: {e}")
            return {
                "action": "error",
                "reason": "无法连接到API服务器，请检查网络",
                "error_type": "connection"
            }
        except APIError as e:
            audit_logger.error(f"API错误: {e}")
            return {
                "action": "error",
                "reason": f"API调用错误: {str(e)}",
                "error_type": "api"
            }
        except json.JSONDecodeError as e:
            audit_logger.error(f"JSON解析失败: {e}")
            return {
                "action": "error",
                "reason": "模型返回了无效的JSON格式",
                "error_type": "json"
            }
        except Exception as e:
            audit_logger.critical(f"未预期的错误: {e}")
            return {
                "action": "error",
                "reason": f"未知错误: {str(e)}",
                "error_type": "unknown"
            }

class Prompts:
    """
    临床定制化 Prompt 集
    """
    @staticmethod
    def extraction():
        """
        场景：医疗化验单结构化数据提取
        """
        return """
        # 任务
        你是一个临床检验数据分析专家。请从覆盖了红色视觉网格的化验单截图中提取指标。
        
        # 提取规范
        1. WBC (白细胞计数): 单位通常为 10^9/L
        2. RBC (红细胞计数): 单位通常为 10^12/L
        3. Hgb (血红蛋白): 单位通常为 g/L
        4. PLT (血小板计数): 单位通常为 10^9/L
        
        # 约束条件
        - 必须交叉核对指标名称及其对应的数值，防止行列错位。
        - 仅提取数值。
        - 如果数值后带有 H/L (高/低) 标志，请忽略标志，只保留数值。
        - 若截图模糊，请在 confidence 字段中如实说明。
        
        # 输出格式 (严格 JSON)
        {
            "thought": "对图像中检验单区域的定位与识别逻辑说明...",
            "findings": [
                {
                    "metric": "WBC",
                    "value": "7.2",
                    "confidence": 0.98,
                    "target_field_hint": "白细胞"
                }
            ],
            "scan_quality": "High/Normal/Low"
        }
        """
    
    @staticmethod
    def operation(task_state):
        """
        场景：基于视觉网格的 UI 自动化录入
        """
        return f"""
        # 任务背景
        你正在操作医院电子病历系统 (EMR)。
        待录入数据内容: {task_state}
        
        # 视觉环境
        屏幕上已叠加 [Set-of-Mark] 红色网格。每个交叉点附近都有标签（如 A1, B2）。
        
        # 决策逻辑
        1. 在屏幕上寻找与待录入指标匹配的输入框位置。
        2. 锁定该输入框在网格中的坐标。
        3. 动作序列：
           - 'click': 点击输入框使其获得焦点。
           - 'type': 输入对应数值。
           - 'finish': 所有数据录入完毕后调用。
        
        # 安全禁令
        - 严禁点击“删除”、“重置”或“处方发送”等危险按钮，除非任务明确要求。
        - 若屏幕弹出任何异常警告（如‘病人ID不匹配’），请立即停止并报告。
        
        # 输出格式 (JSON)
        {{
            "thought": "我发现 WBC 输入框位于网格 C5 区域，准备点击...",
            "action": "click" | "type" | "finish",
            "coordinate": [x, y],
            "text": "打字内容",
            "reasoning": "为什么执行此操作"
        }}
        """
