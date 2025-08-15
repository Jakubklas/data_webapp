#!/usr/bin/env python3
"""
Script to verify the installation directory structure of Flex Controller
Run this after installing the application to check for nested directory issues
"""
import os
from pathlib import Path

def list_directory_tree(path, prefix="", max_depth=10, current_depth=0):
    """Recursively list directory contents with tree structure"""
    if current_depth >= max_depth:
        print(f"{prefix}... (max depth reached)")
        return
    
    try:
        path = Path(path)
        if not path.exists():
            print(f"Path does not exist: {path}")
            return
        
        items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and current_depth < max_depth:
                next_prefix = prefix + ("    " if is_last else "│   ")
                list_directory_tree(item, next_prefix, max_depth, current_depth + 1)
                
    except PermissionError:
        print(f"{prefix}[Permission Denied]")
    except Exception as e:
        print(f"{prefix}[Error: {e}]")

def check_for_nesting_issues(install_path):
    """Check for specific nesting issues"""
    install_path = Path(install_path)
    issues = []
    
    # Check for config file nesting
    nested_config = install_path / "defaults" / "config.toml" / "default_config.toml"
    if nested_config.exists():
        issues.append(f"❌ Config nesting issue: {nested_config}")
    
    correct_config = install_path / "default_config.toml"
    if correct_config.exists():
        print(f"✅ Config file correctly placed: {correct_config}")
    else:
        issues.append(f"❌ Config file missing: {correct_config}")
    
    # Check for Python file nesting in src
    src_path = install_path / "src"
    if src_path.exists():
        print(f"✅ src directory exists: {src_path}")
        
        # Check specific files for nesting
        test_files = [
            "src/utils/general_utils/css.py",
            "src/pages/eoa/upload_page.py",
            "src/pages/eoa/settings_page.py"
        ]
        
        for test_file in test_files:
            file_path = install_path / test_file
            nested_path = install_path / test_file / Path(test_file).name
            
            if file_path.exists() and file_path.is_file():
                print(f"✅ File correctly placed: {file_path}")
            elif nested_path.exists():
                issues.append(f"❌ File nesting issue: {nested_path}")
            else:
                issues.append(f"❌ File missing: {file_path}")
    else:
        issues.append(f"❌ src directory missing: {src_path}")
    
    # Check streamlit_static
    streamlit_static = install_path / "streamlit_static"
    if streamlit_static.exists():
        print(f"✅ streamlit_static correctly placed: {streamlit_static}")
    else:
        issues.append(f"❌ streamlit_static missing: {streamlit_static}")
    
    return issues

def main():
    install_path = r"C:\Program Files\Flex Controller"
    
    print("=" * 60)
    print("FLEX CONTROLLER INSTALLATION VERIFICATION")
    print("=" * 60)
    print(f"Checking installation at: {install_path}")
    print()
    
    # List complete directory structure
    print("COMPLETE DIRECTORY STRUCTURE:")
    print("-" * 40)
    list_directory_tree(install_path, max_depth=6)
    print()
    
    # Check for specific nesting issues
    print("NESTING ISSUE CHECK:")
    print("-" * 40)
    issues = check_for_nesting_issues(install_path)
    
    if not issues:
        print("🎉 NO NESTING ISSUES FOUND!")
        print("Installation appears to be correct.")
    else:
        print(f"⚠️  FOUND {len(issues)} ISSUES:")
        for issue in issues:
            print(f"  {issue}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()