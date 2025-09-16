"""
Simple logger utility for Mini Email CRM
Provides basic logging functionality for the application
"""

import logging
import os
from datetime import datetime


def setup_logger(name="mini_email_crm", level=logging.INFO):
    """
    Set up a logger with console and file output
    
    Args:
        name (str): Logger name
        level: Logging level
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional, only if logs directory exists)
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if os.path.exists(logs_dir) or True:  # Create logs dir if it doesn't exist
        try:
            os.makedirs(logs_dir, exist_ok=True)
            log_file = os.path.join(logs_dir, f'mini_crm_{datetime.now().strftime("%Y%m%d")}.log')
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # If file logging fails, just use console
            pass
    
    return logger