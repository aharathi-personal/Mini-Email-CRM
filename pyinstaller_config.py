"""
Resource bundling configuration for PyInstaller
Handles collection of all application resources
"""

import os
from pathlib import Path

def get_data_files():
    """
    Collect all data files that need to be bundled with the executable
    Returns list of (source, destination) tuples for PyInstaller
    """
    data_files = []
    
    # Configuration files
    config_files = [
        ('config/settings.py', 'config/'),
        ('config/themes.json', 'config/'),
    ]
    
    # Resource directories to include
    resource_dirs = [
        'resources',
        'exports', 
        'logs',
        'models',
        'temp'
    ]
    
    # Add config files
    for src, dst in config_files:
        if os.path.exists(src):
            data_files.append((src, dst))
    
    # Add resource directories
    for dir_name in resource_dirs:
        if os.path.exists(dir_name):
            # Add the entire directory
            data_files.append((f'{dir_name}/*', f'{dir_name}/'))
            
            # Walk through subdirectories
            for root, dirs, files in os.walk(dir_name):
                for file in files:
                    src_path = os.path.join(root, file)
                    # Preserve directory structure
                    rel_path = os.path.relpath(src_path, '.')
                    dst_dir = os.path.dirname(rel_path)
                    data_files.append((src_path, dst_dir + '/'))
    
    return data_files

def get_hidden_imports():
    """
    Get list of modules that need to be explicitly imported
    """
    hidden_imports = [
        # PyQt5 core modules
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'PyQt5.QtPrintSupport',
        'PyQt5.sip',
        'sip',
        
        # Data processing
        'pandas',
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
        'numpy.linalg.lapack_lite',
        'numpy.linalg._umath_linalg',
        
        # Email modules
        'email',
        'email.mime',
        'email.mime.text',
        'email.mime.multipart', 
        'email.mime.base',
        'email.mime.application',
        'smtplib',
        'imaplib',
        'poplib',
        
        # Standard library modules that might be missed
        'csv',
        'json',
        'sqlite3',
        'threading',
        'queue',
        'datetime',
        'pathlib',
        'tempfile',
        'shutil',
        'glob',
        're',
        'urllib',
        'urllib.parse',
        'urllib.request',
        'ssl',
        'socket',
        'zipfile',
        'gzip',
        
        # Application specific modules
        'core',
        'core.email_service',
        'core.campaign_manager',
        'core.template_engine',
        'core.theme_manager',
        'core.csv_handler',
        'core.attachment_cleanup',
        'core.integration_manager',
        'core.validation_pipeline',
        'core.error_handling',
        'ui',
        'utils',
        'models',
        'config',
        'config.settings',
        
        # Environment variables
        'dotenv',
        'python-dotenv',
    ]
    
    return hidden_imports

def get_excluded_modules():
    """
    Modules to exclude from the build to reduce size
    """
    excluded = [
        'matplotlib',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'unittest',
        'doctest',
        'pdb',
        'profile',
        'cProfile',
        'pstats',
    ]
    
    return excluded

# Export for use in spec file
DATA_FILES = get_data_files()
HIDDEN_IMPORTS = get_hidden_imports()
EXCLUDED_MODULES = get_excluded_modules()