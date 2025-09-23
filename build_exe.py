#!/usr/bin/env python3
"""
Build script for Mini Email CRM using PyInstaller
Creates a standalone executable with all dependencies
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_artifacts():
    """Remove previous build artifacts"""
    artifacts = ['build', 'dist', '__pycache__']
    for artifact in artifacts:
        if os.path.exists(artifact):
            print(f"Removing {artifact}...")
            shutil.rmtree(artifact)

def ensure_dependencies():
    """Ensure PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building Mini Email CRM executable...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'mini_email_crm.spec'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Build failed!")
        print(e.stderr)
        return False

def validate_executable():
    """Basic validation of the created executable"""
    exe_path = Path('dist/Mini Email CRM.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"Executable created: {exe_path}")
        print(f"Size: {size_mb:.2f} MB")
        return True
    else:
        print("Executable not found!")
        return False

def main():
    """Main build process"""
    print("Mini Email CRM - PyInstaller Build Script")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Build steps
    steps = [
        ("Cleaning artifacts", clean_build_artifacts),
        ("Checking dependencies", ensure_dependencies),
        ("Building executable", build_executable),
        ("Validating build", validate_executable),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        success = step_func()
        if not success and step_func in [build_executable, validate_executable]:
            print(f"Failed at: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Build completed successfully!")
    print("Executable location: dist/Mini Email CRM.exe")
    print("\nTo distribute:")
    print("1. Test the executable on a clean system")
    print("2. Create installer if needed")
    print("3. Consider code signing for production")

if __name__ == "__main__":
    main()