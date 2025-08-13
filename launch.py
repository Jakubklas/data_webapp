import os, sys, subprocess, socket, time, webbrowser, shutil
from pathlib import Path
from subprocess import CREATE_NO_WINDOW

def _wait(host, port, t=40):
    end = time.time() + t
    while time.time() < end:
        try:
            with socket.create_connection((host, port), 1):
                return True
        except OSError:
            time.sleep(0.4)
    return False

def _ensure_user_config(install_root: Path) -> Path:
    base = Path(os.getenv("LOCALAPPDATA", str(install_root))) / "FlexController" / ".streamlit"
    base.mkdir(parents=True, exist_ok=True)
    dest = base / "config.toml"
    if not dest.exists():
        # Try to find packaged default config file
        packaged_locations = [
            install_root / "defaults" / "config.toml",  # Expected location (if it's a file)
            install_root / "defaults" / "config.toml" / "config.toml",  # If defaults/config.toml is a directory
            install_root / ".streamlit" / "config.toml",  # Alternative location
            install_root / ".streamlit" / ".streamlit" / "config.toml",  # If .streamlit is doubled
        ]
        
        config_copied = False
        for packaged in packaged_locations:
            if packaged.exists() and packaged.is_file():
                try:
                    shutil.copy2(packaged, dest)
                    config_copied = True
                    break
                except (OSError, PermissionError):
                    continue
        
        if not config_copied:
            # Fallback: write a minimal config
            dest.write_text(
                "[global]\n"
                "developmentMode = false\n\n"
                "[server]\n"
                "headless = true\n"
                "port = 8502\n",
                encoding="utf-8",
            )
    return dest


def main():
    # For pynsist installations, the app files are in the same directory as the executable
    # For regular Python, they would be in parent.parent, but pynsist puts them alongside
    exe_dir = Path(sys.executable).resolve().parent
    
    # Try multiple possible locations for app.py to find correct install root
    possible_roots = [
        exe_dir,                    # Same directory as Python executable
        exe_dir.parent,             # One level up from Python executable  
        exe_dir.parent.parent,      # Two levels up (traditional structure)
    ]
    
    install_root = None
    for root in possible_roots:
        # Check for app.py and src directory (handling both normal and doubled directory structure)
        app_exists = (root / "app.py").exists()
        src_exists = (root / "src").exists() or (root / "src" / "src").exists()
        
        if app_exists and src_exists:
            install_root = root
            break
    
    if install_root is None:
        # Emergency fallback - use exe_dir even if app.py doesn't exist there
        install_root = exe_dir
    
    os.chdir(install_root)

    py = Path(sys.executable)
    print(f"Python executable: {py}")
    print(f"App path: {install_root / 'app.py'}")
    print(f"Command: {[str(py), '-m', 'streamlit', 'run', str(install_root / 'app.py')]}")

    # Logs
    log_dir = Path(os.getenv("LOCALAPPDATA", str(install_root))) / "FlexController" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "streamlit.log"

    user_cfg = _ensure_user_config(install_root)

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    env["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_SERVER_PORT"] = "8502"
    # Also pass flags (highest precedence) to guarantee settings
    cmd = [
        str(py), "-m", "streamlit", "run", str(install_root / "app.py"),
        "--global.developmentMode=false",
        "--server.port=8502", "--server.headless=true"
    ]

    with open(log_file, "w", encoding="utf-8") as log:
        log.write(f"Starting Streamlit with command: {cmd}\n")
        log.write(f"Working directory: {install_root}\n")
        log.write(f"Python path: {py}\n")
        log.write(f"exe_dir: {exe_dir}\n")
        log.write(f"Config file: {user_cfg}\n")
        log.write(f"App exists: {(install_root / 'app.py').exists()}\n")
        log.write(f"src directory exists: {(install_root / 'src').exists()}\n")
        log.write(f"upload_page exists: {(install_root / 'src/pages/eoa/upload_page.py').exists()}\n")
        if (install_root / 'src').exists():
            log.write(f"src directory contents: {os.listdir(install_root / 'src')}\n")
        log.write(f"install_root contents: {list(install_root.iterdir())}\n")
        log.flush()
        try:
            subprocess.Popen(
                cmd, cwd=str(install_root), env=env,
                stdout=log, stderr=log, creationflags=CREATE_NO_WINDOW
            )
        except Exception as e:
            log.write(f"Failed to start subprocess: {e}\n")
            log.flush()

    if _wait("127.0.0.1", 8502, t=40):
        webbrowser.open("http://localhost:8502")
    else:
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0, f"Failed to start server.\nSee log:\n{log_file}", "Flex Controller", 0
            )
        except Exception:
            pass
