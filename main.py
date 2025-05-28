import streamlit as st
from config import *
from misc.css import *

def main():
    # Set page configuration
    st.set_page_config(
        page_title=title,
        page_icon = page_icon
        )

    # -----------PAGE SETUP---------------

    pages = {
        "UTILITIES": [
            st.Page("views/other/maestro_script.py",        title="Maestro Script")
        ],
        "SCHEDULING": [
            st.Page("views/scheduling/inputs.py",        title="Scheduling Inputs"),
            st.Page("views/scheduling/tool_2.py",      title="Wave Planning"),
            st.Page("views/scheduling/tool_3.py",        title="SPR Planning"),
            st.Page("views/scheduling/tool_4.py",        title="Schedule Ahead"),
            st.Page("views/scheduling/tool_5.py",        title="UTR Buffers"),
        ],
        "EXCLUSIVE OFFERS": [
            st.Page("views/eoa/eoa_upload.py",   title="Offer Upload"),
            st.Page("views/eoa/eoa_settings.py", title="Configuration")
        ]
    }

    pg = st.navigation(pages, position="sidebar", expanded=True)
    pg.run()

if __name__ == "__main__":
    main()


# python -m streamlit run main.py
