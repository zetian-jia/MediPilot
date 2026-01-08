import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    # OpenAI 配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # 模型配置
    VISION_MODEL = os.getenv("VISION_MODEL", "gpt-4o")
    EXTRACTION_MODEL = os.getenv("EXTRACTION_MODEL", "gpt-4o")
    
    # 系统设置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    SCREENSHOT_DELAY = float(os.getenv("SCREENSHOT_DELAY", 1.0))
    
    # 安全设置
    PAUSE_INTERVAL = 0.8
    FAILSAFE = True

config = Config()
