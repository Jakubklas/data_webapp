import streamlit as st
from components import EOA_Upload_Page, Settings_Page
from config import *
from css import *

def main():
    # Set page configuration
    st.set_page_config(page_title=title)

    st.sidebar.title("Menu")


    if 'page' not in st.session_state:
        st.session_state.page = 'EOA Upload'

    st.markdown(side_bar_buttons, unsafe_allow_html=True)

    if st.sidebar.button("EOA Upload"):
        st.session_state.page = 'EOA Upload'
    if st.sidebar.button("Settings"):
        st.session_state.page = 'Settings'

    page = st.session_state.page
    if page == 'EOA Upload':
        EOA_Upload_Page()
    elif page == 'Settings':
        Settings_Page()

if __name__ == "__main__":
    main()


# python -m streamlit run main.py
