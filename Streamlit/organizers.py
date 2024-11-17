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

def organizer_view():
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 60px; margin-bottom: 50px;"> 🎯 Hackathon Group Finder - Organizer View</h1>
        """,
        unsafe_allow_html=True
    )

    st.header("Upload Participant Data")
    uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])

    if uploaded_file is not None:
        try:
            # Create data directory if it doesn't exist
            data_dir = Path('data')
            data_dir.mkdir(exist_ok=True)

            # Save uploaded file
            file_path = data_dir / uploaded_file.name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getvalue())

            # Read the JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Convert JSON to DataFrame
            df = pd.DataFrame(data)

            # Display data preview
            st.subheader("Data Preview")
            st.dataframe(df.head())

            # Basic statistics
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
                        # Run Script 1
                        st.info("Running text_similarities_indexing...")
                        main1()  # Waits for main1() to finish
                        progress_bar.progress(33)
                        st.success("text_similarities_indexing completed!")
                        time.sleep(2)

                        # Run Script 2
                        st.info("Running text_processing_final...")
                        main2()  # Waits for main2() to finish
                        progress_bar.progress(66)
                        st.success("text_processing_final completed!")
                        time.sleep(2)

                        # Provide download button for processed data
                        processed_file_path = "/data/df_text_processed.csv"
                        if os.path.exists(processed_file_path):
                            with open(processed_file_path, "rb") as f:
                                processed_data = f.read()
                            st.download_button(
                                label="Download Processed Data",
                                data=processed_data,
                                file_name="df_text_processed.csv",
                                mime="text/csv"
                            )
                        else:
                            st.warning("Processed file not found. Please ensure the processing completed successfully.")

                    except Exception as e:
                        st.error(f"Error during group generation: {str(e)}")

