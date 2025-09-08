# Configuration settings for Mini Email CRM
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SMTP Configuration
SMTP_SETTINGS = {
    'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', '587')),
    'use_tls': True,
    'username': os.getenv('SMTP_USERNAME', ''),
    'password': os.getenv('SMTP_PASSWORD', ''),
}

# UI Constants
UI_SETTINGS = {
    'window_title': 'Mini Email CRM',
    'window_width': int(os.getenv('WINDOW_WIDTH', '1000')),
    'window_height': int(os.getenv('WINDOW_HEIGHT', '700')),
    'min_width': int(os.getenv('MIN_WINDOW_WIDTH', '800')),
    'min_height': int(os.getenv('MIN_WINDOW_HEIGHT', '600')),
}

# File Settings
FILE_SETTINGS = {
    'allowed_extensions': ['.csv', '.xlsx', '.xls'],
    'max_file_size_mb': int(os.getenv('MAX_FILE_SIZE_MB', '10')),
    'encoding': os.getenv('FILE_ENCODING', 'utf-8'),
}

# Email Settings
EMAIL_SETTINGS = {
    'batch_size': int(os.getenv('EMAIL_BATCH_SIZE', '50')),
    'delay_between_batches': int(os.getenv('EMAIL_DELAY_BETWEEN_BATCHES', '2')),
    'max_retries': int(os.getenv('EMAIL_MAX_RETRIES', '3')),
    'timeout': int(os.getenv('EMAIL_TIMEOUT', '30')),
}

# Logging Settings
LOGGING_SETTINGS = {
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': 'email_crm.log',
    'max_log_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
}

# Application Settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'