import streamlit as st
import pandas as pd
from config import *

def create_sidebar(text="This is a sample app"):
    with st.sidebar:
        st.header(text)
        st.link_button(label = "Click the link", url = "https://midway-auth.amazon.com/login")

def create_layout():
    # Create headline
    st.title(title)
    
    # Create chat input and display
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def clear_input():
        st.session_state["chat_input"] = ""

    user_input = st.text_input("Enter your message:", key="chat_input", on_change=clear_input)
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

    st.write("Chat history:")
    for msg in st.session_state.chat_history:
        st.write(f"{msg['role'].capitalize()}: {msg['content']}")
    
    # Create output field
    st.write("You entered:", user_input)

    df = pd.DataFrame(data)

    col_1, col_2 = st.columns(spec=[3, 1])

    with col_1:
        edited_df = st.data_editor(df, num_rows="dynamic")

    with col_2:
        st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.\nSed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\nUt enim ad minim veniam, quis nostrud exercitation ullamco.\nLaboris nisi ut aliquip ex ea commodo consequat.",)

    st.subheader("Weekly Revenue")

    st.bar_chart(
        data = edited_df.set_index("Week")["Revenue"],
        use_container_width = True
    )

    create_sidebar(text="A sample")



    