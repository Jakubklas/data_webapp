import streamlit as st
import pandas as pd
import numpy as np
from src.services.inputs_processing import InputsProcessor
from src.s3_utils import get_s3_object, save_to_s3
from src.utils.utils import separate_text_input, confirm_dialog
from src.config import *

def Scheduling_Inputs():
    st.title("Scheduling Inputs")

    if "inputs" not in st.session_state:
        st.session_state.inputs = get_s3_object(scheduling_bucket, "scheduling_inputs.parquet")

### ---------------------- Filters ----------------------

    with st.expander("Filters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            station_filter = st.text_input(
                label="Station",
                placeholder="All"
            )

            cycle_filter = st.multiselect(
                label="Cycle",
                options=list(st.session_state.inputs["cycle"].unique()),
                placeholder="All"
            )

        with col2:
            week_filter = st.multiselect(
                label="Week",
                options=list(st.session_state.inputs["week"].unique()),
                placeholder="All"
            )

            date_filter = st.multiselect(
                label="Date",
                options=list(st.session_state.inputs["ofd_date"].unique()),
                placeholder="All"
            )

        # Filter the dataframe based on the filters
        mask = pd.Series(True, index=st.session_state.inputs.index)
        if station_filter:
            station_list = separate_text_input(station_filter, item_length=4)
            mask &= st.session_state.inputs["station"].isin(station_list)
        if cycle_filter:
            mask &= st.session_state.inputs["cycle"].isin(cycle_filter)
        if week_filter:
            mask &= st.session_state.inputs["week"].isin(week_filter)
        if date_filter:
            mask &= st.session_state.inputs["ofd_date"].isin(date_filter)
    
        filtered_inputs = st.session_state.inputs[mask]

### ---------------------- Original Scheduling Inputs ----------------------

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("Current Data:")
    with col4:
            if st.button(
                label="Manually Sync Data",
                help="Manually synchronize all dependencies to the neweset available data. (Only synchronizes to local Windows file share)"
                ):
                processor = InputsProcessor(scheduling_bucket, local_files)
                try:
                    # Sync all the new data
                    processor.sync()
                    # Process and combine into one file
                    st.session_state.inputs= processor\
                            .process_snop() \
                            .process_co_nd() \
                            .process_co_sd() \
                            .join_forecasts() \
                            .process_scms() \
                            .process_utr() \
                            .process_spr() \
                            .process_sa_table() \
                            .process_waveplan() \
                            .combine_data()
                    st.success("✅ All files have been updated.")
                except Exception as e:
                    st.error(f"Failed to upload all files due to:\n{e}")
    st.dataframe(
        filtered_inputs if 'filtered_inputs' in locals() else st.session_state.inputs,
        hide_index=True
    )

    st.session_state.setdefault("show_confirm", False)
    st.session_state.setdefault("confirmed", False)
    st.session_state.setdefault("saved_overrides", False)

### ---------------------- Confirm Dialog ----------------------

    @st.dialog("⚠️ Please confirm", width="small")
    def confirm_dialog():
        st.write(
            "Are you sure you want to override the scheduling inputs? "
            "This action will impact Flex scheduling."
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, I confirm."):
                st.session_state.confirmed= True
                st.session_state.show_confirm = False
                st.rerun()
        with c2:
            if st.button("No. Go back."):
                st.session_state.confirmed = False
                st.session_state.show_confirm = False
                st.rerun() 

    if st.button("Override Current Inputs"):
        st.session_state.show_confirm = True
        st.session_state.confirmed = False
        st.rerun()

    if st.session_state.show_confirm:
        confirm_dialog()

### ---------------------- Input Overrides ----------------------

    if st.session_state.saved_overrides:
        st.success("Uploaded new Scheduling Inputs")
        # clear it so it only shows once
        st.session_state.saved_overrides = False

    if st.session_state.confirmed:
        st.divider()
        st.subheader("Manually Override Scheduling Inputs:")

        st.session_state.inputs = st.data_editor(
            data=st.session_state.inputs,
            hide_index=True,
            disabled= locked_inputs
            )

        if st.button("Save Overrides"):
            save_to_s3(st.session_state.inputs, scheduling_bucket, "scheduling_inputs.parquet", format="parquet")
            st.session_state.saved_overrides = True
            st.session_state.confirmed = False
            st.rerun()


if __name__ == "__main__":
    Scheduling_Inputs()