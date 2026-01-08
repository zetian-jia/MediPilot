import time
from typing import Dict, Any, List, Optional, Tuple
import pyautogui
from medipilot.utils.logger import audit_logger
from configs.settings import config

class ExecutionError(Exception):
    """执行层异常"""
    pass

class Executor:
    """
    执行层：负责 GUI 操作
    包含安全限速和临床复核逻辑提示。
    
    Attributes:
        screen_size: 屏幕尺寸 (width, height)
    """
    
    def __init__(self) -> None:
        """
        初始化执行器，配置安全参数
        
        Raises:
            ExecutionError: 初始化失败时抛出
        """
        try:
            # 初始化 PyAutoGUI 安全设置
            pyautogui.PAUSE = config.PAUSE_INTERVAL
            pyautogui.FAILSAFE = config.FAILSAFE
            
            # 获取屏幕尺寸用于坐标验证
            self.screen_size: Tuple[int, int] = pyautogui.size()
            
            audit_logger.info(
                f"执行模块初始化完成 | 屏幕尺寸: {self.screen_size} | "
                f"紧急熔断(FAILSAFE): {'启用' if config.FAILSAFE else '禁用'}"
            )
        except Exception as e:
            audit_logger.critical(f"执行模块初始化失败: {e}")
            raise ExecutionError(f"无法初始化GUI自动化: {e}")
    
    def _validate_coordinate(self, coord: Optional[List[int]]) -> bool:
        """
        验证坐标的有效性
        
        Args:
            coord: 坐标列表 [x, y]
            
        Returns:
            bool: 坐标是否有效
        """
        if not coord or not isinstance(coord, (list, tuple)):
            audit_logger.warning("坐标格式错误：不是列表或元组")
            return False
        
        if len(coord) != 2:
            audit_logger.warning(f"坐标格式错误：长度为 {len(coord)}，期望为 2")
            return False
        
        x, y = coord
        screen_w, screen_h = self.screen_size
        
        if not (0 <= x <= screen_w and 0 <= y <= screen_h):
            audit_logger.warning(
                f"坐标越界: ({x}, {y})，屏幕尺寸: ({screen_w}, {screen_h})"
            )
            return False
        
        return True

    def execute(self, plan: Dict[str, Any]) -> bool:
        """
        根据认知层计划执行动作
        
        Args:
            plan: 模型生成的指令，包含 action, coordinate, text 等
            
        Returns:
            bool: 任务是否结束
            
        Raises:
            pyautogui.FailSafeException: 用户触发紧急停止时抛出
        """
        action = plan.get("action", "unknown")
        coord = plan.get("coordinate")
        text = plan.get("text")
        reasoning = plan.get("reasoning", "未注明原因")
        
        # 处理错误状态
        if action == "error":
            error_reason = plan.get("reason", "未知错误")
            error_type = plan.get("error_type", "unknown")
            audit_logger.error(f"无法执行 [{error_type}]: {error_reason}")
            
            # 根据错误类型决定是否继续
            if error_type in ["rate_limit", "connection"]:
                audit_logger.info("等待5秒后继续...")
                time.sleep(5)
            return False
        
        audit_logger.info(f"执行动作: [{action.upper()}] | 理由: {reasoning}")
        
        try:
            if action == "click":
                if not self._validate_coordinate(coord):
                    audit_logger.error("点击动作坐标无效，跳过执行")
                    return False
                
                x, y = coord
                # 临床环境建议平滑移动，避免突兀点击
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                audit_logger.info(f"✓ 点击坐标: ({x}, {y})")
                
            elif action == "type":
                if not self._validate_coordinate(coord):
                    audit_logger.error("输入动作坐标无效，跳过执行")
                    return False
                
                if not text:
                    audit_logger.warning("输入动作缺少文本内容")
                    return False
                
                x, y = coord
                # 先点击确保聚焦
                pyautogui.click(x, y)
                time.sleep(0.2)  # 等待输入框获得焦点
                
                # 模拟人类打字速度
                text_str = str(text)
                pyautogui.write(text_str, interval=0.1)
                audit_logger.info(f"✓ 输入文本: '{text_str}' 于坐标 ({x}, {y})")
                
            elif action == "scroll":
                # 支持滚动操作
                amount = plan.get("amount", -500)
                pyautogui.scroll(amount)
                audit_logger.info(f"✓ 滚动页面: {amount}")
                
            elif action == "wait":
                # 支持等待操作
                duration = plan.get("duration", 2)
                audit_logger.info(f"等待 {duration} 秒...")
                time.sleep(duration)
                
            elif action == "finish":
                audit_logger.info("=" * 60)
                audit_logger.info("✓ 任务执行完毕")
                audit_logger.info("⚠️  请医师进行最终审核！")
                audit_logger.info("=" * 60)
                # 在实际临床场景中，此处可弹出确认对话框
                return True
                
            else:
                audit_logger.warning(f"未知的动作类型: '{action}'，跳过执行")
                
        except pyautogui.FailSafeException:
            audit_logger.warning("🛑 用户触发紧急停止（FAILSAFE）")
            raise
        except Exception as e:
            audit_logger.error(f"执行动作时发生错误: {e}")
            # 不抛出异常，而是继续执行
            
        return False
