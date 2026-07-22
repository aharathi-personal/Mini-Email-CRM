# PyInstaller spec file for Mini Email CRM
# Generated template - tweak datas/hiddenimports as needed

# NOTE: This spec is a template. Replace/confirm the icon file path (Windows requires .ico)
# and the resources you want bundled.

from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

# Entry script
entry_script = 'main.py'

# Extra data trees: include resources, ui templates, config files
datas = [
    ('resources', 'resources'),
    ('ui', 'ui'),
    ('config', 'config'),
]

# Hidden imports can be collected automatically for some libs (PyQt5 sometimes needs hints)
hiddenimports = collect_submodules('PyQt5')

a = Analysis(
    [entry_script],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='Mini Email CRM',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='resources/icons/app_icon.ico'  # Provide a .ico file for Windows builds
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='Mini Email CRM'
)
