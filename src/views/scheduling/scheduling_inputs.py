import streamlit as st
import pandas as pd
import numpy as np
from src.services.inputs_processing import InputsProcessor
from aws_utils.s3_utils import get_s3_object, save_to_s3
from src.utils.utils import separate_text_input, confirm_dialog, overrides_widget
from src.utils.css import overrides_widget_styling
from config import *

def Scheduling_Inputs():
    st.title("Scheduling Inputs")

    if "inputs" not in st.session_state:
        st.session_state.inputs = get_s3_object(scheduling_bucket, "scheduling_inputs.parquet")

    
### ---------------------- Checking for Overrides ----------------------
    def get_overrides():
        try:
            return get_s3_object(scheduling_bucket, "overrides_layer.parquet")
        except ValueError as e:
            if "No objects found in the prefix" in str(e):
                return None
            else:
                raise
        except Exception:
            raise

    st.session_state.setdefault("overrides_layer", get_overrides())
### ---------------------- Filter Section ----------------------

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

    st.session_state.setdefault("show_confirm", False)
    st.session_state.setdefault("confirmed", False)
    st.session_state.setdefault("saved_overrides", False)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.session_state.confirmed:
            st.subheader("Override Mode:")
        else:
            st.subheader("Current Inputs:")
    with col3:
            if st.session_state.confirmed:
                if st.button("Save Overrides", use_container_width=True):
                    save_to_s3(st.session_state.overrides_layer, scheduling_bucket, "overrides_layer.parquet", format="parquet")
                    st.session_state.saved_overrides = True
                    st.session_state.confirmed = False
                    st.rerun()                
            else:
                if st.button(
                    label="Manually Sync Data",
                    help="Manually synchronize all dependencies to the neweset available data. (Only synchronizes to local Windows file share)",
                    use_container_width=True
                    ):
                    processor = InputsProcessor(scheduling_bucket, local_files)
                    try:
                        with st.spinner("Syncing with local files"):    
                            processor.sync()
                        with st.spinner("Processing data"):    
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
                        with col4:
                            st.success("✅ All files have been updated.")
                    except Exception as e:
                        st.error(f"Failed to upload all files due to:\n{e}")
    with col4:
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

        if st.session_state.confirmed:
            if st.button("Cancel", use_container_width=True):
                st.session_state.overrides_layer = get_overrides()          # TODO: Clear any accumulated overrides in the session + default to what's in S3
                st.session_state.confirmed = False
                st.rerun() 
        else:
            if st.button("Override Current Inputs", use_container_width=True):
                st.session_state.show_confirm = True
                st.session_state.confirmed = False
                st.rerun()

        if st.session_state.show_confirm:
            confirm_dialog()


###---------------------- Table Section ----------------------

    if st.session_state.confirmed:

        overrides = st.data_editor(
            data=filtered_inputs,
            hide_index=True,
            disabled= locked_inputs
            )
        
        # Saving Overrides (edited rows) in a variable
        if overrides is not None:
            original = st.session_state.inputs.loc[overrides.index, overrides.columns]
            orig_filled = original.fillna("__NULL__")
            ov_filled   = overrides.fillna("__NULL__")

            mask = (ov_filled != orig_filled).any(axis=1)
            overriden_rows = overrides.loc[mask]
            st.session_state.overrides_layer = overriden_rows
        
    else:
        st.dataframe(
            filtered_inputs if 'filtered_inputs' in locals() else st.session_state.inputs,
            hide_index=True
        )

###---------------------- Overrides Section ----------------------
    st.divider()
    st.subheader("Active Overrides")

    if st.session_state.overrides_layer is not None:
        if st.session_state.overrides_layer.shape[0] != 0:
            # st.dataframe(
            #     st.session_state.overrides_layer,
            #     hide_index=True
            # )
            st.markdown(overrides_widget_styling, unsafe_allow_html=True)
            overrides_widget(st.session_state.overrides_layer)            
        else:
            st.write("There are not active manual overrides at the moment.")
    else:
        st.write("There are not active manual overrides at the moment.")


        



if __name__ == "__main__":
    Scheduling_Inputs()