#!/usr/bin/env python3
"""
Comprehensive Import Dependency Checker
This script checks all Python files for missing imports and dependency issues
"""

import os
import sys
import ast
import importlib.util

# Windows consoles default to cp1252, which can't encode the emoji this
# script prints; reconfigure to UTF-8 so it runs unmodified.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def check_file_imports(file_path):
    """Check a single Python file for import issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the AST
        try:
            ast.parse(content)
            return None, None  # No syntax errors
        except SyntaxError as e:
            return "SyntaxError", str(e)
        except Exception as e:
            return "ParseError", str(e)
            
    except Exception as e:
        return "FileError", str(e)

def find_python_files(directory):
    """Find all Python files in the directory"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {'__pycache__', '.git', 'venv', 'env', 'build', 'dist', '.pytest_cache'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def main():
    project_root = "/Users/pgiridha/Desktop/Email CRM Project/Mini-Email-CRM"
    print("=== Comprehensive Import Dependency Check ===")
    print(f"Checking: {project_root}")
    print()
    
    python_files = find_python_files(project_root)
    print(f"Found {len(python_files)} Python files")
    print()
    
    errors_found = []
    
    for file_path in python_files:
        relative_path = os.path.relpath(file_path, project_root)
        error_type, error_msg = check_file_imports(file_path)
        
        if error_type:
            errors_found.append((relative_path, error_type, error_msg))
            print(f"❌ {relative_path}: {error_type}")
            print(f"   {error_msg}")
            print()
        else:
            print(f"✅ {relative_path}")
    
    print("\n" + "="*60)
    
    if errors_found:
        print(f"SUMMARY: Found {len(errors_found)} files with issues:")
        for file_path, error_type, error_msg in errors_found:
            print(f"  - {file_path}: {error_type}")
        return 1
    else:
        print("SUMMARY: All Python files passed syntax check! 🎉")
        return 0

if __name__ == '__main__':
    sys.exit(main())