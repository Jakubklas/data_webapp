import streamlit as st
from config import *
from css    import *
def main():
    # Set page configuration
    st.set_page_config(
        page_title=title,
        page_icon = page_icon
        )
    
    # -----------PAGE SETUP---------------

    with st.sidebar:
        st.header("Menu")

    pages = {
        "UTILITIES": [
            st.Page("views/other/maestro_script.py",        title="Maestro Script",    icon="🗓️")
        ],
        "SCHEDULING": [
            st.Page("views/scheduling/tool_1.py",        title="Scheduling Inputs",    icon="🗓️"),
            st.Page("views/scheduling/tool_2.py",      title="Wave Planning",        icon="⚙️")
        ],
        "EXCLUSIVE OFFERS": [
            st.Page("views/eoa/eoa_upload.py",   title="Offer Upload",     icon="📥"),
            st.Page("views/eoa/eoa_settings.py", title="Configuration",  icon="⚙️")
        ]
    }

    pg = st.navigation(pages, position="sidebar", expanded=True)
    pg.run()

if __name__ == "__main__":
    main()


# python -m streamlit run main.py
