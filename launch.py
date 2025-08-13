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
        # copy packaged default if present, else write a minimal one
        packaged = install_root / "defaults" / "config.toml"
        if packaged.exists():
            shutil.copy2(packaged, dest)
        else:
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
    install_root = Path(sys.executable).resolve().parent.parent
    os.chdir(install_root)

    py = Path(sys.executable).with_name("python.exe")
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

    env["STREAMLIT_CONFIG_FILE"] = str(user_cfg)
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
        try:
            subprocess.Popen(
                cmd, cwd=str(install_root), env=env,
                stdout=log, stderr=log, creationflags=CREATE_NO_WINDOW
            )
        except Exception as e:
            log.write(f"Failed to start subprocess: {e}\n")

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
