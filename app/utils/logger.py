"""
日志配置工具
"""

import logging
import logging.handlers
import os
import sys


def setup_logger(name: str = 'code996', log_dir: str = './logs') -> logging.Logger:
    """
    配置日志
    
    Args:
        name: logger名称
        log_dir: 日志目录
    
    Returns:
        配置好的logger对象
    """
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建 logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 文件 handler (按日期轮转)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'app.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # 格式化
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加 handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

