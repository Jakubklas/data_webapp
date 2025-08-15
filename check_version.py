#!/usr/bin/env python3
"""
Flex Controller Version Checker
Helps identify which version is currently installed and running
"""
import os
import sys
from pathlib import Path

def check_installation_locations():
    """Check common installation locations for Flex Controller"""
    
    common_locations = [
        Path("C:/Program Files/Flex Controller"),
        Path("C:/Program Files (x86)/Flex Controller"), 
        Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs/Flex Controller"),
        Path(os.path.expanduser("~/AppData/Local/Programs/Flex Controller")),
        Path(os.path.expanduser("~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Flex Controller")),
    ]
    
    print("=== Scanning for Flex Controller installations ===")
    print()
    
    found_installations = []
    
    for location in common_locations:
        if location.exists():
            print(f"FOUND: {location}")
            
            # Check for key files
            app_py = location / "app.py"
            launch_py = location / "launch.py"
            src_dir = location / "src"
            
            print(f"  - app.py: {'YES' if app_py.exists() else 'NO'}")
            print(f"  - launch.py: {'YES' if launch_py.exists() else 'NO'}")
            print(f"  - src/: {'YES' if src_dir.exists() else 'NO'}")
            
            # Check for .streamlit directory (shouldn't exist in new version)
            streamlit_dir = location / ".streamlit"
            if streamlit_dir.exists():
                print(f"  - .streamlit/: EXISTS (OLD VERSION - should be removed)")
            else:
                print(f"  - .streamlit/: NOT PRESENT (good)")
            
            # Check for defaults directory (should exist in new version)
            defaults_dir = location / "defaults"
            if defaults_dir.exists():
                print(f"  - defaults/: EXISTS (new version)")
            else:
                print(f"  - defaults/: MISSING (might be old version)")
                
            found_installations.append(location)
            print()
        else:
            print(f"NOT FOUND: {location}")
    
    return found_installations

def check_logs():
    """Check the log files for version information"""
    
    log_locations = [
        Path(os.getenv("LOCALAPPDATA", "")) / "FlexController" / "logs" / "streamlit.log",
        Path.home() / "AppData" / "Local" / "FlexController" / "logs" / "streamlit.log"
    ]
    
    print("=== Checking log files ===")
    print()
    
    for log_path in log_locations:
        if log_path.exists():
            print(f"Log found: {log_path}")
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extract version info if present
                    lines = content.split('\n')
                    for line in lines[:10]:  # Check first 10 lines
                        if "Flex Controller v" in line:
                            print(f"  Version: {line.strip()}")
                        elif "Build Date:" in line or "Build ID:" in line or "Launch Time:" in line:
                            print(f"  {line.strip()}")
                        elif "Working directory:" in line:
                            print(f"  {line.strip()}")
                            break
                            
            except Exception as e:
                print(f"  Error reading log: {e}")
            print()
        else:
            print(f"No log at: {log_path}")

def check_running_processes():
    """Check if any Flex Controller processes are running"""
    print("=== Checking running processes ===")
    print()
    
    try:
        import subprocess
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
            capture_output=True, text=True, shell=True
        )
        
        if "python.exe" in result.stdout:
            print("Python processes found - may include Flex Controller")
            # You could add more specific process detection here
        else:
            print("No Python processes found")
            
    except Exception as e:
        print(f"Could not check processes: {e}")

if __name__ == "__main__":
    print("Flex Controller Installation Checker")
    print("=" * 50)
    print()
    
    installations = check_installation_locations()
    print()
    
    check_logs()
    print()
    
    check_running_processes()
    print()
    
    print("=== Summary ===")
    if installations:
        print(f"Found {len(installations)} installation(s)")
        print("To ensure you're running the latest version:")
        print("1. Check the log file for version info")
        print("2. Look for 'defaults/' directory (new version)")  
        print("3. Ensure no '.streamlit/' directory exists (old version)")
        print("4. Uninstall old versions if multiple found")
    else:
        print("No installations found in common locations")