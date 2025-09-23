# PyInstaller hook for Mini Email CRM PyQt5 requirements
# This hook ensures all necessary PyQt5 components are included

import os
try:
    from PyInstaller.utils.hooks import collect_data_files, collect_submodules
except ImportError:
    # Fallback if PyInstaller is not available during linting
    def collect_data_files(module_name):
        return []
    def collect_submodules(module_name):
        return []

# Collect all PyQt5 data files
datas = collect_data_files('PyQt5')

# Hidden imports for PyQt5 modules that might be missed
hiddenimports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.QtPrintSupport',
    'PyQt5.QtNetwork',
    'PyQt5.QtSvg',
    'PyQt5.sip',
    'sip',
]

# Include PyQt5 plugins
def get_pyqt5_library_info():
    """Get PyQt5 library information for proper packaging"""
    try:
        from PyQt5.QtCore import QLibraryInfo
        return {
            'plugins_path': QLibraryInfo.location(QLibraryInfo.PluginsPath),
            'translations_path': QLibraryInfo.location(QLibraryInfo.TranslationsPath),
        }
    except ImportError:
        return None

# Add Qt plugins that might be needed
qt_plugins = [
    'platforms',
    'imageformats', 
    'iconengines',
    'styles',
]

pyqt_info = get_pyqt5_library_info()
if pyqt_info:
    for plugin in qt_plugins:
        try:
            plugin_path = os.path.join(pyqt_info['plugins_path'], plugin)
            if os.path.exists(plugin_path):
                datas.append((plugin_path, f'PyQt5/Qt/plugins/{plugin}'))
        except Exception:
            # Silently ignore plugin collection errors
            pass