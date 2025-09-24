# Configuration settings for Mini Email CRM
import os


def _get_int_env(key: str, default: int) -> int:
    """Get an integer environment variable with safe fallback.

    Returns the integer value of the env var, or the provided default if parsing fails.
    """
    val = os.getenv(key, str(default))
    try:
        return int(val)
    except (ValueError, TypeError):
        return int(default)


def _get_bool_env(key: str, default: bool) -> bool:
    """Get a boolean environment variable with safe fallback."""
    val = os.getenv(key, str(default))
    try:
        return str(val).lower() in ('1', 'true', 'yes', 'on')
    except Exception:
        return bool(default)

# SMTP Configuration
SMTP_SETTINGS = {
    'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'port': _get_int_env('SMTP_PORT', 587),
    'use_tls': True,
    # NOTE: Do NOT load username/password from environment here.
    # Credentials should be provided at runtime via the Login UI
    # and injected into the application (e.g. MainWindow.on_login_success).
    # Keep these blank by default to avoid using any .env-supplied secrets
    # as the authoritative credentials for a session.
    'username': '',
    'password': '',
}

# UI Constants
UI_SETTINGS = {
    'window_title': 'Mini Email CRM',
    'window_width': _get_int_env('WINDOW_WIDTH', 1000),
    'window_height': _get_int_env('WINDOW_HEIGHT', 700),
    'min_width': _get_int_env('MIN_WINDOW_WIDTH', 800),
    'min_height': _get_int_env('MIN_WINDOW_HEIGHT', 600),
}

# File Settings
FILE_SETTINGS = {
    'allowed_extensions': ['.csv', '.xlsx', '.xls'],
    'max_file_size_mb': _get_int_env('MAX_FILE_SIZE_MB', 10),
    'encoding': os.getenv('FILE_ENCODING', 'utf-8'),
}

# Email Settings
EMAIL_SETTINGS = {
    'batch_size': _get_int_env('EMAIL_BATCH_SIZE', 50),
    'delay_between_batches': _get_int_env('EMAIL_DELAY_BETWEEN_BATCHES', 2),
    'max_retries': _get_int_env('EMAIL_MAX_RETRIES', 3),
    'timeout': _get_int_env('EMAIL_TIMEOUT', 30),
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
DEBUG = _get_bool_env('DEBUG', False)