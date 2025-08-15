#!/usr/bin/env python3
"""
Verify that all Flex Controller installations have been removed
"""
import os
from pathlib import Path

def verify_cleanup():
    print("=== Verifying Cleanup ===")
    print()
    
    locations_to_check = [
        Path("C:/Program Files/Flex Controller"),
        Path("C:/Program Files (x86)/Flex Controller"), 
        Path(os.path.expanduser("~/AppData/Local/Programs/Flex Controller")),
    ]
    
    print("Checking installation directories:")
    all_clean = True
    
    for location in locations_to_check:
        if location.exists():
            print(f"⚠️  STILL EXISTS: {location}")
            all_clean = False
        else:
            print(f"✓  CLEANED: {location}")
    
    print()
    print("Checking user data:")
    user_data = Path(os.getenv("LOCALAPPDATA", "")) / "FlexController"
    if user_data.exists():
        print(f"📁 USER DATA EXISTS: {user_data}")
        print("   (This is OK - contains logs and config)")
        if (user_data / "logs").exists():
            print("   - Contains logs")
        if (user_data / ".streamlit").exists():
            print("   - Contains user config")
    else:
        print("✓  USER DATA CLEANED")
    
    print()
    if all_clean:
        print("🎉 CLEANUP COMPLETE! Ready for fresh installation.")
    else:
        print("⚠️  Some installations still exist. Admin rights may be needed.")
        
    return all_clean

if __name__ == "__main__":
    verify_cleanup()