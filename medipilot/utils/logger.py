import logging
import os
from datetime import datetime
from configs.settings import config

def setup_logger(name="MediPilot"):
    """
    配置临床审计日志记录器
    
    功能:
    1. 记录所有自动化操作步骤，用于事后追溯 (Audit Trail)。
    2. 区分常规操作信息 (INFO) 和 潜在风险警告 (WARNING).
    3. 日志文件按日期归档，便于医院信息科管理。
    """
    # 确保日志目录存在
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 日志文件名: medipilot_YYYY-MM-DD.log
    log_file = os.path.join(log_dir, f"medipilot_{datetime.now().strftime('%Y-%m-%d')}.log")

    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)

    # 避免重复添加 handler
    if not logger.handlers:
        # 文件处理器 - 用于存档
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - [临床操作审计] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # 控制台处理器 - 用于实时监控
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

audit_logger = setup_logger()
