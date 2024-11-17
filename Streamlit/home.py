# Import statements
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import time
import plotly.graph_objects as go
from pathlib import Path
from text_similarities_indexing import main as main1
from text_processing_final import main as main2

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Group generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for bigger buttons
st.markdown("""
    <style>
    div.stButton > button {
        font-size: 24px;
        height: 120px;
        width: 100%;
        background-color: #28948c;
        color: white;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #B3B8B6;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    div.stButton > button:active {
        transform: translateY(0px);
    }
    </style>
""", unsafe_allow_html=True)


def role_selection():
    # Creates a large centered title at the top of the page
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 80px; margin-bottom: 60px;"> Group Generator</h1>
        """, 
        unsafe_allow_html=True
    )
    
    # Creates a smaller subtitle asking users about their role
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 23px; font-weight: normal; margin-bottom: 40px;">Hey there! What is your profile?</h1>
        """, 
        unsafe_allow_html=True
    )

    # Adds vertical spacing
    st.markdown("<br>", unsafe_allow_html=True)

    # Creates a layout with two columns and a small space between them
    col1, space, col2 = st.columns([1, 0.2, 1])
    
    # In the left column, creates a "participant" button
    with col1:
        if st.button("I'm a participant 👤"):
            st.session_state.page = 'participant'  # Updates the session state
            st.rerun()  # Refreshes the page to show participant view
    
    # In the right column, creates an "organizer" button
    with col2:
        if st.button("I'm an organizer 👥"):
            st.session_state.page = 'organizer'  # Updates the session state
            st.rerun()  # Refreshes the page to show organizer view


def save_uploaded_file(uploaded_file):
    """Save uploaded file and return the file path"""
    # Create data directory if it doesn't exist
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Save file
    file_path = data_dir / uploaded_file.name
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getvalue())
    
    return file_path

def process_dataset(df):
    """Process the dataset and return results"""
    try:
        # Basic data validation
        required_columns = ['name', 'skills', 'preferences']  # Add your required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return None
            
        # Add your group generation logic here
        # For now, returning basic statistics
        results = {
            'total_participants': len(df),
            'skill_distribution': df['skills'].value_counts().to_dict(),
            'groups': []  # Add your group generation results here
        }
        
        return results
        
    except Exception as e:
        st.error(f"Error processing dataset: {str(e)}")
        return None

def organizer_view():
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 60px; margin-bottom: 50px;"> 🎯 Hackathon Group Finder - Organizer View</h1>
        """,
        unsafe_allow_html=True
    )
    
    # Create tabs for different organizer functions
    tab1, tab2, tab3 = st.tabs(["Upload Data", "View Groups", "Settings"])
    
    with tab1:
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
                
                # Create three separate buttons for each script
                st.subheader("Generate Groups Process")
                
                # Button for Script 1
                if st.button("1. Run Text Similarities Indexing"):
                    with st.spinner("Running text_similarities_indexing..."):
                        try:
                            main1()
                            st.success("Text similarities indexing completed!")
                            # Set a flag in session state to track completion
                            st.session_state['script1_complete'] = True
                        except Exception as e:
                            st.error(f"Error in text similarities indexing: {str(e)}")
                
                # Button for Script 2
                if st.button("2. Run Text Processing"):
                    if st.session_state.get('script1_complete', False):
                        with st.spinner("Running text_processing_final..."):
                            try:
                                main2()
                                st.success("Text processing completed!")
                                # Set a flag in session state to track completion
                                st.session_state['script2_complete'] = True
                            except Exception as e:
                                st.error(f"Error in text processing: {str(e)}")
                    else:
                        st.warning("Please complete Step 1 (Text Similarities Indexing) first.")
                
                # Button for Script 3
                if st.button("3. Generate Final Groups"):
                    if st.session_state.get('script2_complete', False):
                        with st.spinner("Generating final groups..."):
                            try:
                                output_csv = process_script3(st.session_state['participant_data'])
                                st.success("Final groups generated!")
                                
                                # Provide download link for Script 3 output
                                st.markdown("### Download Generated Groups")
                                st.download_button(
                                    label="Download CSV",
                                    data=output_csv.to_csv(index=False),
                                    file_name="generated_groups.csv",
                                    mime="text/csv",
                                )
                            except Exception as e:
                                st.error(f"Error generating final groups: {str(e)}")
                    else:
                        st.warning("Please complete Steps 1 and 2 first.")
                
            except Exception as e:
                st.error(f"Error processing the uploaded file: {str(e)}")
                return
    

def display_results_with_download(results, filename):
    """Display results and provide download options"""
    st.subheader("Processing Results")
    
    # Display basic statistics
    st.write(f"Total Participants: {results['total_participants']}")
    
    # Create and display skills distribution chart
    fig = px.bar(
        x=list(results['skill_distribution'].keys()),
        y=list(results['skill_distribution'].values()),
        title="Skills Distribution"
    )
    st.plotly_chart(fig)
    
    # Provide download option
    if st.button("Download Results"):
        # Convert results to CSV or Excel
        results_df = pd.DataFrame(results['groups'])
        
        # Save and provide download link
        output_path = f"data/results_{filename}"
        results_df.to_csv(output_path, index=False)
        
        with open(output_path, 'rb') as f:
            st.download_button(
                label="Download Results File",
                data=f,
                file_name=f"results_{filename}",
                mime="text/csv"
            )


def participant_view():
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 60px; margin-bottom: 50px;">🎯 Hackathon Group Finder</h1>
        """, 
        unsafe_allow_html=True
    )
    
    # Add participant form
    with st.form("participant_form"):
        name = st.text_input("Your Name")
        skills = st.multiselect(
            "Select your skills",
            ["Python", "Data Analysis", "Machine Learning", "Web Development", "Design"]
        )
        preferences = st.text_area("Additional Preferences")
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            # Process participant data
            participant_data = {
                "name": name,
                "skills": skills,
                "preferences": preferences
            }
            
            # Save to session state or file
            if 'participants' not in st.session_state:
                st.session_state.participants = []
            st.session_state.participants.append(participant_data)
            
            st.success("Thank you for submitting! You'll be notified when groups are formed.")

def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'role_selection'
    
    # Route to appropriate page
    if st.session_state.page == 'role_selection':
        role_selection()
    elif st.session_state.page == 'organizer':
        organizer_view()
    elif st.session_state.page == 'participant':
        participant_view()

if __name__ == "__main__":
    main()