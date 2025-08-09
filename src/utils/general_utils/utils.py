import streamlit as st
import pandas as pd
from datetime import timezone
from config import *
from aws_utils.s3_utils import save_to_s3, list_s3_objects
from src.utils.css import overrides_widget_styling

def process_sa(df):
    report = {}

    # Verify Columns
    for col in df.columns:
        if col not in sa_columns:
            report["column_check"] = False
        else:
            report["column_check"] = True

    # Count offers, stations, durations
    report["offers"] = df.shape[0]
    report["stations"] = df["Station"].nunique()
    report["avg_duration"] = df["Duration"].mean()

    return report
    

def separate_text_input(text, item_length=None):
    try:
        if len(text) == item_length:
            separator = None
        elif "," in text:
            separator = ","
        elif ", " in text:
            separator = ", "
        elif " " in text:
            separator = " "
        elif "\n" in text:
            separator = "\n"
        elif "\t" in text:
            separator = "\t"

        result = text.split(sep=separator)
        outliers = [item for item in result if len(item) != item_length]

        if len(outliers) != 0:
            st.error(f"Items not found: {outliers}")

        return result
    except Exception as e:
        st.error(f"Unexpected text format. Separate values by commas, spaces, new-lines, or tabs. \n {e}")


@st.dialog("⚠️ Please confirm", width="small")
def confirm_dialog(session_variable, message, yes, no):
    st.write(message)
    c1, c2 = st.columns(2)
    with c1:
        if st.button(yes):
            session_variable = True
            return session_variable
            st.rerun()
    with c2:
        if st.button(no):
            session_variable = False
            st.stop()
            return session_variable


def overrides_widget(overrides_df: pd.DataFrame):
    st.markdown(overrides_widget_styling, unsafe_allow_html=True)
    if overrides_df is None or overrides_df.empty:
        st.write("There are no active manual overrides at the moment.")
        return

    col1, col2 = st.columns([9,1])

    for idx, row in overrides_df.iterrows():
        # Build a bold title via Markdown **...**
        title = f"**{row['day']}, W{row['week']}   /   {row['ofd_date']}   /   {row['station']}   /   {row['cycle']}**"

        with st.container():
            with col1:
                # Each expander will inherit the CSS we injected above
                with st.expander(title, expanded=False):
                    cols = st.columns([1, 0.1, 1, 0.1, 1])
                    cols[0].write(f"**Value:** {row['value']}")
                    cols[4].write(f"**Station:** {row['station']}")
                    # Show any other columns below if you like
                    leftover = [c for c in overrides_df.columns if c not in ["day","week","ofd_date","station","cycle","value","wave_demand"]]
                    for key in leftover:
                        st.write(f"**{key}:** {row[key]}")
            with col2:
                st.button("✖️", key=idx)

    # Draw a final separator
    st.markdown("---")

