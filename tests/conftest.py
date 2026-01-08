"""
Pytest 配置文件
定义全局fixtures和测试配置
"""
import pytest
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def test_env():
    """设置测试环境变量"""
    original_env = {}
    
    # 保存原始环境变量
    for key in ['OPENAI_API_KEY', 'VISION_MODEL', 'LOG_LEVEL']:
        original_env[key] = os.environ.get(key)
    
    # 设置测试环境变量
    os.environ['OPENAI_API_KEY'] = 'sk-test-key-for-testing-only'
    os.environ['VISION_MODEL'] = 'gpt-4o'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    yield
    
    # 恢复原始环境变量
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

@pytest.fixture
def mock_config():
    """模拟配置对象"""
    class MockConfig:
        OPENAI_API_KEY = "sk-test-key"
        OPENAI_BASE_URL = "https://api.openai.com/v1"
        VISION_MODEL = "gpt-4o"
        EXTRACTION_MODEL = "gpt-4o"
        LOG_LEVEL = "INFO"
        SCREENSHOT_DELAY = 1.0
        PAUSE_INTERVAL = 0.8
        FAILSAFE = True
        PRIVACY_REGION = (0, 150, 0, 400)
        
    return MockConfig()

@pytest.fixture
def sample_medical_data():
    """模拟医疗数据"""
    return {
        "thought": "检测到化验单数据",
        "findings": [
            {"metric": "WBC", "value": "7.2", "unit": "10^9/L", "confidence": 0.98},
            {"metric": "RBC", "value": "4.8", "unit": "10^12/L", "confidence": 0.95},
            {"metric": "Hgb", "value": "142", "unit": "g/L", "confidence": 0.97},
            {"metric": "PLT", "value": "210", "unit": "10^9/L", "confidence": 0.96}
        ],
        "scan_quality": "High"
    }

@pytest.fixture
def sample_action_plan():
    """模拟操作计划"""
    return {
        "thought": "发现WBC输入框",
        "action": "click",
        "coordinate": [450, 600],
        "text": None,
        "reasoning": "点击输入框以获得焦点"
    }