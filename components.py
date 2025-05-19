import streamlit as st
import pandas as pd
from config import *

def create_layout():
    # Create headline
    st.title(title)
    
    # Create input field
    user_input = st.text_input("Enter your text here:\n")
    
    # Create output field
    st.write("You entered:", user_input)

    df = pd.DataFrame(data)

    st.subheader("Weekly Revenue")

    st.bar_chart(
        data = df.set_index("Week")["Revenue"],
        use_container_width = True
    )
