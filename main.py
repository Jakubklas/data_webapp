import streamlit as st
from components import create_layout, create_sidebar
from config import *

def main():
    # Set page configuration
    st.set_page_config(page_title=title)
    
    # Call the layout function
    create_layout()

    # Call the sidebar finction
    create_sidebar()

if __name__ == "__main__":
    main()


# python -m streamlit run main.py
