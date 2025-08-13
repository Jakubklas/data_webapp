import streamlit as st
import pandas as pd
from datetime import timezone
import config as cfg
from src.utils.general_utils.css import overrides_widget_styling


def verify_eoa_upload(df):
    """
    Checks the correct colmns are in place and
    creates a mini file overview for user before
    uploading to S3 for offer matching.
    """
    report = {}

        for col in df.columns:
        if col not in cfg.sa_columns:
            report["Column Check"] = False
        else:
            report["Column Check"] = True

        report["Offers"] = df.shape[0]
    report["Stations"] = df["Station"].nunique()
    report["Cycles"] = "".join([c + " / " for c in df["Cycle"].unique()])[:-2]
    report["Date Range"] = f"{df['OFD Date'].min().strftime("%y-%m-%d")} - {df['OFD Date'].max().strftime("%y-%m-%d")}"
    report["Avg. Block Lenght"] = df["Duration"].mean()

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
                title = f"**{row['day']}, W{row['week']}   /   {row['ofd_date']}   /   {row['station']}   /   {row['cycle']}**"

        with st.container():
            with col1:
                                with st.expander(title, expanded=False):
                    cols = st.columns([1, 0.1, 1, 0.1, 1])
                    cols[0].write(f"**Value:** {row['value']}")
                    cols[4].write(f"**Station:** {row['station']}")
                                        leftover = [c for c in overrides_df.columns if c not in ["day","week","ofd_date","station","cycle","value","wave_demand"]]
                    for key in leftover:
                        st.write(f"**{key}:** {row[key]}")
            with col2:
                st.button("✖️", key=idx)

        st.markdown("---")

