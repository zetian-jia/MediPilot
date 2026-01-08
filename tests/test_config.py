"""
MediPilot 配置系统单元测试
"""
import pytest
import os
from configs.settings import Config, ConfigError

class TestConfig:
    """配置系统测试类"""
    
    def test_config_initialization(self):
        """测试配置初始化"""
        config = Config()
        assert hasattr(config, 'OPENAI_API_KEY')
        assert hasattr(config, 'VISION_MODEL')
        assert hasattr(config, 'PRIVACY_REGION')
    
    def test_default_values(self):
        """测试默认值"""
        config = Config()
        assert config.OPENAI_BASE_URL == "https://api.openai.com/v1"
        assert config.VISION_MODEL == "gpt-4o" or os.getenv("VISION_MODEL")
        assert config.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert config.SCREENSHOT_DELAY > 0
        assert config.PAUSE_INTERVAL > 0
        assert config.FAILSAFE is True
    
    def test_privacy_region_format(self):
        """测试隐私区域格式"""
        config = Config()
        assert isinstance(config.PRIVACY_REGION, tuple)
        assert len(config.PRIVACY_REGION) == 4
        y1, y2, x1, x2 = config.PRIVACY_REGION
        assert y1 < y2
        assert x1 < x2
    
    def test_validate_with_missing_api_key(self, monkeypatch):
        """测试缺少API密钥时的验证"""
        # 临时移除API密钥
        monkeypatch.setattr(Config, 'OPENAI_API_KEY', '')
        
        with pytest.raises(ConfigError) as exc_info:
            Config.validate()
        
        assert "OPENAI_API_KEY 未配置" in str(exc_info.value)
    
    def test_validate_with_invalid_api_key(self, monkeypatch):
        """测试无效API密钥格式"""
        # 设置错误格式的密钥
        monkeypatch.setattr(Config, 'OPENAI_API_KEY', 'invalid-key-format')
        
        with pytest.raises(ConfigError) as exc_info:
            Config.validate()
        
        assert "API 密钥格式错误" in str(exc_info.value)
    
    def test_validate_with_invalid_log_level(self, monkeypatch):
        """测试无效日志级别"""
        monkeypatch.setattr(Config, 'LOG_LEVEL', 'INVALID')
        
        with pytest.raises(ConfigError) as exc_info:
            Config.validate()
        
        assert "无效的日志级别" in str(exc_info.value)
    
    def test_validate_with_invalid_delay(self, monkeypatch):
        """测试无效的延迟参数"""
        monkeypatch.setattr(Config, 'SCREENSHOT_DELAY', -1.0)
        
        with pytest.raises(ConfigError) as exc_info:
            Config.validate()
        
        assert "SCREENSHOT_DELAY 必须大于 0" in str(exc_info.value)
    
    def test_validate_with_invalid_privacy_region(self, monkeypatch):
        """测试无效的隐私区域"""
        # y1 >= y2
        monkeypatch.setattr(Config, 'PRIVACY_REGION', (100, 50, 0, 400))
        
        with pytest.raises(ConfigError) as exc_info:
            Config.validate()
        
        assert "PRIVACY_REGION 坐标无效" in str(exc_info.value)
    
    def test_display_info(self, capsys):
        """测试配置信息显示"""
        config = Config()
        config.display_info()
        
        captured = capsys.readouterr()
        assert "MediPilot 配置信息" in captured.out
        assert "视觉模型" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])