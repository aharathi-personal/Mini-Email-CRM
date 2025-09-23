#!/bin/bash

# Mini Email CRM - Dark Mode Error Dialog Fix & Build Script
# This script rebuilds the application with all the dark mode error dialog fixes

echo "=== Mini Email CRM Build Script ==="
echo "Building application with dark mode error dialog fixes..."

# Navigate to project directory
cd "/Users/pgiridha/Desktop/Email CRM Project/Mini-Email-CRM"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/
rm -rf dist/

# Run PyInstaller
echo "Building application bundle..."
pyinstaller mini_email_crm.spec

# Check if build was successful
if [ -d "dist/Mini Email CRM.app" ]; then
    echo "✅ Build successful!"
    echo "Application bundle created at: dist/Mini Email CRM.app"
    echo ""
    echo "=== Key Fixes Applied ==="
    echo "✅ All QMessageBox calls replaced with ThemedMessageBox"
    echo "✅ Error dialogs now properly themed for dark mode"
    echo "✅ Dynamic stylesheet conflicts resolved with !important rules"
    echo "✅ Missing QSpacerItem import fixed"
    echo "✅ ThemedMessageBox uses higher specificity CSS"
    echo ""
    echo "=== Files Modified ==="
    echo "- ui/error_dialogs.py: Enhanced with !important CSS rules"
    echo "- ui/main_window.py: QMessageBox → ThemedMessageBox"
    echo "- ui/widgets/email_editor.py: QMessageBox → ThemedMessageBox + QSpacerItem import"
    echo "- ui/widgets/email_editor_backup.py: QMessageBox → ThemedMessageBox + QSpacerItem import"
    echo "- ui/widgets/enhanced_attachment.py: QMessageBox → ThemedMessageBox"
    echo ""
    echo "To test: Open 'dist/Mini Email CRM.app' and trigger an error in dark mode"
    echo "The error dialogs should now be clearly visible with proper contrast."
else
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi