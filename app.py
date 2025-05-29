import streamlit as st
from src.config import *
from src.utils.css import *

def main():
    
    # Set page configuration
    st.set_page_config(
        page_title=title,
        page_icon = page_icon,
        layout="wide"
        )
    
    st.markdown(wide_page, unsafe_allow_html=True)
    # -----------PAGE SETUP---------------

    pages = {
        "UTILITIES": [
            st.Page("src/views/other/maestro_script.py",        title="Maestro Script")
        ],
        "SCHEDULING": [
            st.Page("src/views/scheduling/scheduling_inputs.py",        title="Scheduling Inputs"),
            st.Page("src/views/scheduling/tool_2.py",      title="Wave Planning"),
            st.Page("src/views/scheduling/tool_3.py",        title="SPR Planning"),
            st.Page("src/views/scheduling/tool_4.py",        title="Schedule Ahead"),
            st.Page("src/views/scheduling/tool_5.py",        title="UTR Buffers"),
        ],
        "EXCLUSIVE OFFERS": [
            st.Page("src/views/eoa/eoa_upload.py",   title="Offer Upload"),
            st.Page("src/views/eoa/eoa_settings.py", title="Configuration")
        ]
    }

    pg = st.navigation(pages, position="sidebar", expanded=True)
    pg.run()

if __name__ == "__main__":
    main()


# python -m streamlit run app.py
