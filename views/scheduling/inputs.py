import streamlit as st
from utils.inputs_processing import InputsProcessor
from s3_utils import get_s3_object
from config import *

def Scheduling_Inputs():
    st.title("Scheduling Inputs")

    if "inputs" not in st.session_state:
        st.session_state.inputs = get_s3_object(scheduling_bucket, "scheduling_inputs.parquet")

    if st.button(
            label="Manually Sync Data",
            help="Manually synchronize all dependencies to the neweset available data. (Only synchronizes to local Windows file share)"
        ):
        processor = InputsProcessor(scheduling_bucket, local_files)
        try:
            # Sync all the new data
            # processor.sync()
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
            st.success("✅ {}/{} files have been updated.")
        except Exception as e:
            st.error(f"Failed to upload all files due to:\n{e}")

    editable_cols = [
        'wave_capacity', 'wave_start_time', 'wave_frequency', 'wave_end_time',
        'wave_max', 'flex_share_cvp', 'flex_spr_cvp', 'utr_buffer', 'calc_spr', 'D_1', 'D_2', 'D_3',
        'D_4', 'D_5', 'D_6', 'D_7', 'D_8', 'D_9', 'D_10', 'D_11', 'D_12',
        'D_13', 'D_14', 'D_15', 'C_1', 'C_2', 'C_3', 'C_4', 'C_5', 'C_6', 'C_7',
        'C_8', 'C_9', 'C_10', 'C_11', 'C_12', 'C_13', 'C_14', 'C_15']
    
    st.subheader("Current Data:")
    st.dataframe(
        st.session_state.inputs,
        hide_index=True
    )

















if __name__ == "__main__":
    Scheduling_Inputs()