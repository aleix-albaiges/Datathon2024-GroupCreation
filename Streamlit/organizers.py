import streamlit as st
import json
import pandas as pd
import os
import plotly.express as px
import time
import plotly.graph_objects as go
from pathlib import Path
from text_similarities_indexing import main as main1
from text_processing_final import main as main2
from Preprocessing import main as main3
from cluster_optimization import main as main4

def organizer_view():
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 60px; margin-bottom: 50px;"> 🎯 Hackathon Group Finder - Organizer View</h1>
        """,
        unsafe_allow_html=True
    )

    st.header("Upload Participant Data")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Home"):
            st.session_state.page = 'role_selection'
            st.rerun()

    uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])

    if uploaded_file is not None:
        try:
            data_dir = Path('data')
            data_dir.mkdir(exist_ok=True)

            file_path = data_dir / uploaded_file.name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getvalue())

            with open(file_path, 'r') as f:
                data = json.load(f)

            df = pd.DataFrame(data)

            st.subheader("Data Preview")
            st.dataframe(df.head())

            st.subheader("Dataset Statistics")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Participants", len(df))

            with col2:
                if 'skills' in df.columns:
                    unique_skills = df['skills'].str.split(',').explode().nunique()
                    st.metric("Unique Skills", unique_skills)

            # Save to session state
            st.session_state['participant_data'] = df

        except Exception as e:
            st.error(f"Error processing the uploaded file: {str(e)}")
            return


        # Button to generate groups
        if st.button("Generate Groups"):
            with st.spinner("Generating optimal groups..."):
                progress_bar = st.progress(0)

                if 'participant_data' in st.session_state:
                    try:
                        st.info("Running text_similarities_indexing...")
                        main1()  
                        progress_bar.progress(25)
                        st.success("text_similarities_indexing completed!")
                        time.sleep(1)

                        st.info("Running text_processing_final...")
                        main2()  
                        progress_bar.progress(50)
                        st.success("text_processing_final completed!")
                        time.sleep(1)

                        st.info("Running preprocessing...")
                        main3()
                        progress_bar.progress(75)
                        st.success("preprocessing completed!")
                        time.sleep(1)

                        st.info("Running cluster_optimization...")
                        main4()
                        progress_bar.progress(100)
                        st.success("cluster_optimization completed!")
                        time.sleep(1)

                        # Debug: Show current working directory
                        #st.write(f"Current working directory: {os.getcwd()}")

                        # Use absolute or corrected path
                        #processed_file_path = os.path.join(os.getcwd(), "data", "best_groups.json")

                        # Check if file exists
                        if os.path.exists("data/best_groups.json"):
                            with open("data/best_groups.json", "rb") as f:
                                processed_data = f.read()
                            st.download_button(
                                label="Download Processed Data",
                                data=processed_data,
                                file_name="best_groups.json",
                                mime="text/json"
                            )
                        else:
                            st.warning("Processed file not found. Please ensure the processing completed successfully.")

                    except Exception as e:
                        st.error(f"Error during group generation: {str(e)}")
    st.rerun()

