import streamlit as st
from components import create_layout

def main():
    # Set page configuration
    st.set_page_config(page_title="Simple WebApp")
    
    # Call the layout function
    create_layout()

if __name__ == "__main__":
    main()

"""
python -m streamlit run main.py
"""