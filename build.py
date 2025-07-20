#!/usr/bin/env python3
"""
Simple build launcher for com0com GUI Manager
Imports and runs the actual build script directly in the current terminal.
"""

import os
import sys

def main():
    """Import and run the build script from the scripts directory."""
    script_path = os.path.join("scripts", "build.py")
    
    if not os.path.exists(script_path):
        print("❌ Error: Build script not found at scripts/build.py")
        sys.exit(1)
    
    print("🚀 Launching build script...")
    print("=" * 40)
    print()
    
    try:
        # Add scripts directory to Python path
        scripts_dir = os.path.join(os.getcwd(), "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        # Import and run the build module directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_script", script_path)
        build_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build_module)
        
        # Call the main function directly
        build_module.main()
        
    except KeyboardInterrupt:
        print("\n⚠️  Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running build script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()