#!/usr/bin/env python3
"""
PyInstaller Build Script for com0com GUI Manager
Creates a single executable with UAC elevation for Windows.

Run from project root directory: python scripts/build.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Build configuration
BUILD_NAME = "com0com-gui"
MAIN_SCRIPT = "main.py"
ICON_PATH = "assets/icons/app_icon.ico"
DIST_DIR = "dist"
BUILD_DIR = "build"
WORK_DIR = "build/work"

def ensure_project_root():
    """Ensure we're running from the project root directory."""
    # Check if we're in the scripts directory
    current_dir = os.getcwd()
    if os.path.basename(current_dir) == "scripts":
        # Change to parent directory (project root)
        os.chdir("..")
        print(f"📁 Changed to project root: {os.getcwd()}")
    
    # Verify we're in the correct location
    if not os.path.exists(MAIN_SCRIPT):
        print(f"❌ Error: {MAIN_SCRIPT} not found!")
        print("Please run this script from the project root directory:")
        print("  python scripts/build.py")
        sys.exit(1)
    
    # Verify assets directory exists
    if not os.path.exists("assets"):
        print(f"❌ Error: assets directory not found!")
        print("Please ensure you're in the project root directory with assets/ folder")
        sys.exit(1)

def clean_build_dirs():
    """Clean previous build artifacts."""
    print("🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = [DIST_DIR, BUILD_DIR]
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"   Removed {dir_path}/")
    
    # Remove spec file if it exists
    spec_file = f"{BUILD_NAME}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"   Removed {spec_file}")

def create_uac_manifest():
    """Create UAC manifest for Administrator privileges."""
    print("🔒 Creating UAC manifest for Administrator privileges...")
    
    manifest_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="X86"
    name="com0com-gui"
    type="win32"
  />
  <description>com0com Virtual Serial Port Manager</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>'''
    
    # Create manifest in project root to avoid path issues
    manifest_path = "com0com-gui.manifest"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    
    print(f"   Created {manifest_path}")
    return manifest_path

def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Building executable with PyInstaller...")
    
    # Verify required files exist
    if not os.path.exists(MAIN_SCRIPT):
        print(f"❌ Error: {MAIN_SCRIPT} not found!")
        return False
    
    if not os.path.exists(ICON_PATH):
        print(f"⚠️  Warning: {ICON_PATH} not found! Building without icon.")
        icon_arg = []
    else:
        icon_arg = ["--icon", ICON_PATH]
    
    # PyInstaller command arguments (simplified)
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # Windows GUI app (no console)
        "--name", BUILD_NAME,           # Executable name
        "--clean",                      # Clean cache
        "--noconfirm",                  # Overwrite without confirmation
        
        # Asset bundling
        "--add-data", "assets;assets",  # Include entire assets directory
        "--add-data", "src;src",        # Include source code (for imports)
        
        # Windows-specific options
        "--uac-admin",                  # UAC elevation (built-in PyInstaller option)
        
        # PyQt6 specific options
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui", 
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "PyQt6.QtSvg",      # For SVG icon support
        "--hidden-import", "PyQt6.sip",
        
        # Additional hidden imports for your application
        "--hidden-import", "src.gui.main_window",
        "--hidden-import", "src.core.command_manager",
        "--hidden-import", "src.core.config_manager",
        "--hidden-import", "src.utils.constants",
        
        # Main script
        MAIN_SCRIPT
    ]
    
    # Add icon if available
    cmd.extend(icon_arg)
    
    # Remove None values from command
    cmd = [arg for arg in cmd if arg is not None]
    
    print("   Running PyInstaller with command:")
    print(f"   {' '.join(cmd)}")
    print()
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ PyInstaller completed successfully!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller failed with error code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found! Please install it with:")
        print("   pip install -r scripts/requirements-build.txt")
        return False

def verify_build():
    """Verify the build was successful."""
    print("🔍 Verifying build...")
    
    exe_path = os.path.join(DIST_DIR, f"{BUILD_NAME}.exe")
    
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"✅ Executable created successfully!")
        print(f"   📍 Location: {exe_path}")
        print(f"   📏 Size: {file_size_mb:.1f} MB")
        print(f"   🔒 UAC: Administrator privileges required")
        
        # Check if assets are bundled (by file size - should be substantial)
        if file_size_mb > 50:  # PyQt6 apps are typically large
            print(f"   📦 Assets: Likely bundled (large file size)")
        else:
            print(f"   ⚠️  Assets: May not be properly bundled (small file size)")
        
        return True
    else:
        print(f"❌ Executable not found at {exe_path}")
        return False

def print_usage_instructions():
    """Print instructions for using the built executable."""
    print("\n" + "="*60)
    print("🎉 BUILD COMPLETE!")
    print("="*60)
    print(f"Your executable is ready: {DIST_DIR}/{BUILD_NAME}.exe")
    print()
    print("📋 Usage Instructions:")
    print("1. Copy the .exe file to your target Windows machine")
    print("2. Right-click the .exe and select 'Run as administrator'")
    print("   (Or it will automatically prompt for UAC elevation)")
    print("3. The GUI will launch with full driver management privileges")
    print()
    print("⚠️  Important Notes:")
    print("- Administrator privileges are REQUIRED for driver operations")
    print("- The executable includes all assets and dependencies")
    print("- No additional files or installations needed on target machine")
    print("- Compatible with Windows 7, 8, 10, and 11")
    print()
    print("🔧 Build artifacts are located in:")
    print(f"   - Executable: {DIST_DIR}/")
    print(f"   - Build files: {BUILD_DIR}/")
    print()

def main():
    """Main build process."""
    print("🚀 com0com GUI Manager - PyInstaller Build Script")
    print("="*55)
    print()
    
    # Check if running as administrator (warn but don't fail)
    import ctypes
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin:
            print("⚠️  WARNING: Running as Administrator")
            print("   PyInstaller recommends running from a normal terminal")
            print("   The build may still work, but consider running as regular user")
            print()
    except:
        pass  # Non-Windows or can't check
    
    # Ensure we're in the project root
    ensure_project_root()
    
    # Step 1: Clean previous builds
    clean_build_dirs()
    print()
    
    # Step 2: Build executable
    if not build_executable():
        print("\n❌ Build failed! Please check the errors above.")
        sys.exit(1)
    
    print()
    
    # Step 3: Verify build
    if not verify_build():
        print("\n❌ Build verification failed!")
        sys.exit(1)
    
    # Step 4: Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    main()