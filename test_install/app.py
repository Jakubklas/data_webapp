import streamlit as st
import config as cfg
import src
import src.utils.general_utils.css as css
from pathlib import Path
import os

def find_src_path():
    """Find the correct path to src directory, handling doubled directories"""
    current_dir = Path(os.getcwd())
    
    possible_paths = [
        "src/pages/eoa/upload_page.py",
        "src/src/pages/eoa/upload_page.py",
    ]
    
    for path in possible_paths:
        if (current_dir / path).exists():
            return path.replace("/upload_page.py", "").replace("\\upload_page.py", "")
    
    return "src/pages/eoa"

def main():
    
    st.set_page_config(
        page_title=cfg.title,
        page_icon = "icon.ico",
        layout="wide"
        )
    
    st.markdown(css.wide_page, unsafe_allow_html=True)

    src_base = find_src_path()
    
    pages = {
        "EXCLUSIVE OFFERS": [
            st.Page(f"{src_base}/upload_page.py",   title="Offer Upload"),
            st.Page(f"{src_base}/settings_page.py", title="Configuration")
        ]
    }

    pg = st.navigation(pages, position="sidebar", expanded=True)
    pg.run()

if __name__ == "__main__":
    main()


