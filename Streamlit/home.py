# Import statements
import streamlit as st
import json
import pandas as pd
import os
import plotly.express as px
import time
import plotly.graph_objects as go
from pathlib import Path
import organizers  as org


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
        org.organizer_view()
    elif st.session_state.page == 'participant':
        participant_view()

if __name__ == "__main__":
    main()