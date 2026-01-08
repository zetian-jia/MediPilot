import os
import sys
from typing import Tuple
from dotenv import load_dotenv

# 加载 .env 环境变量
load_dotenv()

class ConfigError(Exception):
    """配置错误异常"""
    pass

class Config:
    """
    全局配置类
    包含：模型参数、安全阈值、临床免责声明
    
    Attributes:
        OPENAI_API_KEY (str): OpenAI API密钥
        OPENAI_BASE_URL (str): API基础URL
        VISION_MODEL (str): 视觉理解模型名称
        EXTRACTION_MODEL (str): 数据提取模型名称
        LOG_LEVEL (str): 日志级别
        SCREENSHOT_DELAY (float): 截屏间隔（秒）
        PAUSE_INTERVAL (float): 动作执行间隔（秒）
        FAILSAFE (bool): 紧急熔断开关
        PRIVACY_REGION (Tuple[int, int, int, int]): 隐私保护区域
        DISCLAIMER_TEXT (str): 法律免责声明
    """
    
    # --- OpenAI / 模型连接配置 ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # --- 模型选择 ---
    # 视觉模型：用于理解屏幕 UI 和化验单 (建议 GPT-4o 或 Claude 3.5 Sonnet)
    VISION_MODEL: str = os.getenv("VISION_MODEL", "gpt-4o")
    # 提取模型：用于结构化数据处理
    EXTRACTION_MODEL: str = os.getenv("EXTRACTION_MODEL", "gpt-4o")
    
    # --- 系统运行参数 ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    # 截屏采样间隔 (秒) - 避免过快操作导致系统卡顿
    SCREENSHOT_DELAY: float = float(os.getenv("SCREENSHOT_DELAY", "1.0"))
    
    # --- 隐私与安全配置 (核心) ---
    # 动作执行间隔 (秒) - 模拟人类操作节奏，避免被系统识别为脚本
    PAUSE_INTERVAL: float = 0.8
    # 紧急熔断机制: 鼠标移动到屏幕角落时强制停止
    FAILSAFE: bool = True
    
    # 隐私保护区域 (ROI): [y1, y2, x1, x2]
    # 默认覆盖左上角病人信息区。实际部署时需根据医院 EMR 系统布局调整。
    PRIVACY_REGION: Tuple[int, int, int, int] = (0, 150, 0, 400)

    # --- 法律与临床免责声明 ---
    DISCLAIMER_TEXT: str = """
    【严正声明 / DISCLAIMER】
    1. 本软件 (MediPilot) 仅作为临床辅助工具，用于自动化繁琐的录入工作。
    2. 软件提供的所有数据提取和操作建议，**必须** 经过执业医师的人工复核。
    3. 严禁将本软件用于无人监管的自动诊疗决策。
    4. 开发者不对因未复核导致的医疗差错承担法律责任。
    
    继续使用即代表您已知悉并同意上述条款。
    """
    
    @classmethod
    def validate(cls) -> None:
        """
        验证配置的有效性
        
        Raises:
            ConfigError: 配置验证失败时抛出
        """
        # 验证 API 密钥
        if not cls.OPENAI_API_KEY:
            raise ConfigError(
                "OPENAI_API_KEY 未配置。请在 .env 文件中设置您的 API 密钥。"
            )
        
        if not cls.OPENAI_API_KEY.startswith('sk-'):
            raise ConfigError(
                f"API 密钥格式错误: '{cls.OPENAI_API_KEY[:10]}...'。"
                "OpenAI API 密钥应以 'sk-' 开头。"
            )
        
        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL.upper() not in valid_log_levels:
            raise ConfigError(
                f"无效的日志级别: '{cls.LOG_LEVEL}'。"
                f"有效值: {', '.join(valid_log_levels)}"
            )
        
        # 验证时间参数
        if cls.SCREENSHOT_DELAY <= 0:
            raise ConfigError(
                f"SCREENSHOT_DELAY 必须大于 0，当前值: {cls.SCREENSHOT_DELAY}"
            )
        
        if cls.PAUSE_INTERVAL <= 0:
            raise ConfigError(
                f"PAUSE_INTERVAL 必须大于 0，当前值: {cls.PAUSE_INTERVAL}"
            )
        
        # 验证隐私区域
        y1, y2, x1, x2 = cls.PRIVACY_REGION
        if not (0 <= y1 < y2 and 0 <= x1 < x2):
            raise ConfigError(
                f"PRIVACY_REGION 坐标无效: {cls.PRIVACY_REGION}。"
                "格式应为 (y1, y2, x1, x2)，且 y1 < y2, x1 < x2"
            )
        
        # 验证模型名称
        valid_models = [
            "gpt-4o", "gpt-4-turbo", "gpt-4-vision-preview",
            "claude-3-5-sonnet", "claude-3-opus"
        ]
        if cls.VISION_MODEL not in valid_models:
            print(f"⚠️  警告: 未知的视觉模型 '{cls.VISION_MODEL}'。"
                  f"推荐使用: {', '.join(valid_models[:3])}")
    
    @classmethod
    def display_info(cls) -> None:
        """显示当前配置信息（不包含敏感信息）"""
        masked_key = cls.OPENAI_API_KEY[:7] + "..." + cls.OPENAI_API_KEY[-4:] if cls.OPENAI_API_KEY else "未设置"
        
        print("=" * 60)
        print("MediPilot 配置信息")
        print("=" * 60)
        print(f"API 密钥: {masked_key}")
        print(f"API 地址: {cls.OPENAI_BASE_URL}")
        print(f"视觉模型: {cls.VISION_MODEL}")
        print(f"日志级别: {cls.LOG_LEVEL}")
        print(f"截屏间隔: {cls.SCREENSHOT_DELAY}秒")
        print(f"隐私区域: {cls.PRIVACY_REGION}")
        print(f"紧急熔断: {'启用' if cls.FAILSAFE else '禁用'}")
        print("=" * 60)

# 创建全局配置实例
config = Config()

# 程序启动时自动验证配置（可选，根据需要启用）
# config.validate()
