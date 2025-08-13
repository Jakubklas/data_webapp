import streamlit as st
import config as cfg
import src
import src.utils.general_utils.css as css
def main():
    
    # Set page configuration
    st.set_page_config(
        page_title=cfg.title,
        page_icon = "icon.ico",
        layout="wide"
        )
    
    st.markdown(css.wide_page, unsafe_allow_html=True)
    # -----------PAGE SETUP---------------

    pages = {
        "EXCLUSIVE OFFERS": [
            st.Page("src/pages/eoa/upload_page.py",   title="Offer Upload"),
            st.Page("src/pages/eoa/settings_page.py", title="Configuration")
        ]
    }

    pg = st.navigation(pages, position="sidebar", expanded=True)
    pg.run()

if __name__ == "__main__":
    main()


# python -m streamlit run app.py
