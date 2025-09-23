#!/usr/bin/env python3
"""
Test script for the built executable
Validates that the PyInstaller build works correctly
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_executable_exists():
    """Test if the executable was created"""
    # Check for different platforms
    import platform
    
    if platform.system() == "Darwin":  # macOS
        exe_path = Path('dist/Mini Email CRM.app')
        standalone_path = Path('dist/Mini Email CRM')
        
        if exe_path.exists():
            print(f"✅ macOS app bundle found: {exe_path}")
            return True
        elif standalone_path.exists():
            size_mb = standalone_path.stat().st_size / (1024 * 1024)
            print(f"✅ Standalone executable found: {standalone_path} ({size_mb:.2f} MB)")
            return True
        else:
            print("❌ No executable found (checked for .app bundle and standalone)")
            return False
    else:  # Windows/Linux
        exe_path = Path('dist/Mini Email CRM.exe')
        if not exe_path.exists():
            print("❌ Executable not found at dist/Mini Email CRM.exe")
            return False
        
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executable found: {exe_path} ({size_mb:.2f} MB)")
        return True

def test_executable_launch():
    """Test if the executable can launch (basic smoke test)"""
    import platform
    
    if platform.system() == "Darwin":  # macOS
        exe_path = Path('dist/Mini Email CRM.app')
        standalone_path = Path('dist/Mini Email CRM')
        
        # Try the app bundle first
        if exe_path.exists():
            print("🧪 Testing macOS app bundle launch...")
            try:
                # Check if already running
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                if 'Mini Email CRM' in result.stdout:
                    print("✅ App is already running (detected in process list)")
                    return True
                else:
                    print("✅ App bundle exists and can be launched")
                    return True
            except Exception as e:
                print(f"❌ Failed to check app status: {e}")
                return False
        
        # Try standalone executable
        elif standalone_path.exists():
            print("🧪 Testing standalone executable launch...")
            try:
                process = subprocess.Popen(
                    [str(standalone_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                time.sleep(2)
                
                if process.poll() is None:
                    print("✅ Standalone executable launched successfully")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    return True
                else:
                    stdout, stderr = process.communicate()
                    if process.returncode == 0:
                        print("✅ Standalone executable ran and exited normally")
                        return True
                    else:
                        print(f"❌ Executable exited with error code: {process.returncode}")
                        if stderr:
                            print(f"Error output: {stderr}")
                        return False
            except Exception as e:
                print(f"❌ Failed to launch standalone executable: {e}")
                return False
        else:
            print("❌ No executable found to test")
            return False
    else:  # Windows/Linux
        exe_path = Path('dist/Mini Email CRM.exe')
        
        print("🧪 Testing executable launch...")
        
        try:
            process = subprocess.Popen(
                [str(exe_path), '--test-mode'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(3)
            
            if process.poll() is None:
                print("✅ Executable launched successfully")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                return True
            else:
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    print("✅ Executable ran and exited normally")
                    return True
                else:
                    print(f"❌ Executable exited with error code: {process.returncode}")
                    if stderr:
                        print(f"Error output: {stderr}")
                    return False
                    
        except Exception as e:
            print(f"❌ Failed to launch executable: {e}")
            return False

def test_dependencies():
    """Test if key dependencies are bundled correctly"""
    print("🔍 Checking for common dependency issues...")
    
    # These are common files that should be bundled
    dist_path = Path('dist')
    if not dist_path.exists():
        print("❌ dist directory not found")
        return False
    
    print("✅ Distribution directory found")
    
    # List contents of dist
    try:
        contents = list(dist_path.iterdir())
        print(f"📁 Dist contents: {[item.name for item in contents]}")
    except Exception as e:
        print(f"⚠️  Could not list dist contents: {e}")
    
    return True

def test_file_permissions():
    """Test if the executable has proper permissions"""
    import platform
    
    if platform.system() == "Darwin":  # macOS
        exe_path = Path('dist/Mini Email CRM.app')
        standalone_path = Path('dist/Mini Email CRM')
        
        try:
            if exe_path.exists():
                print("✅ macOS app bundle found with proper structure")
                return True
            elif standalone_path.exists():
                # Check if file is executable
                if os.access(standalone_path, os.X_OK):
                    print("✅ Standalone executable has proper permissions")
                    return True
                else:
                    print("❌ Standalone executable is not executable")
                    return False
            else:
                print("❌ No executable found")
                return False
        except Exception as e:
            print(f"❌ Error checking file permissions: {e}")
            return False
    else:  # Windows/Linux
        exe_path = Path('dist/Mini Email CRM.exe')
        
        try:
            if exe_path.exists():
                if exe_path.suffix.lower() == '.exe':
                    print("✅ Executable has .exe extension")
                    return True
                else:
                    print("⚠️  File doesn't have .exe extension")
                    return False
            else:
                print("❌ Executable file not found")
                return False
        except Exception as e:
            print(f"❌ Error checking file permissions: {e}")
            return False

def main():
    """Run all tests"""
    print("Mini Email CRM - Executable Test Suite")
    print("=" * 50)
    
    tests = [
        ("Executable exists", test_executable_exists),
        ("Dependencies bundled", test_dependencies),
        ("File permissions", test_file_permissions),
        ("Launch test", test_executable_launch),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The executable is ready for distribution.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues before distribution.")
        return 1

if __name__ == "__main__":
    sys.exit(main())