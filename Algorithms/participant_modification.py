# Import statements
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from rich import print
import numpy as np
import math
import ast
from dataclasses import dataclass
from collections import defaultdict
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
import random
from participant import load_participants
import pickle

import pickle
def save_pickle(variable, path: str):
    try:
        with open(path, 'wb') as handle:
            pickle.dump(variable, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return 'ok!'
    except Exception as err:
        print("An error occurred!!!: " + str(err))

        
def load_pickle(path):
    try:
        with open(path, 'rb') as handle:
            return pickle.load(handle)
    except Exception as err:
        print("An error occurred!!!: " + str(err))
        return None

data_path = "datathon_participants.json"

participants_sencer = load_participants(data_path)

id_nom : dict[str,str] = {}

id_email : dict[str,str] = {}

nom_id : dict[str,str] = {}

id_preference : dict[str, int] = {}

for p in participants_sencer:

    id_nom[str(p.id)] = p.name

    id_email[str(p.id)] = p.email

    nom_id[str(p.name)] = str(p.id)

    id_preference[p.name] = p.preferred_team_size

best_groups_set : dict[int,list[set[str]]] = {}
best_groups = load_pickle("best_groups.pickle")
for n, group_size in best_groups.items():
    best_groups_set[n] = []
    for groups in group_size:
        best_groups_set[n].append(set(groups))



# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Group generator",
    page_icon="",
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

# Initialize session state if not already done
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

def initialize_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'role_selection'
    if 'optimal_groups.json' not in st.session_state:
        if Path('optimal_groups.json').exists():
            with open('optimal_groups.json', 'r') as f:
                st.session_state['optimal_groups.json'] = json.load(f)
        else:
            st.session_state['optimal_groups.json'] = None

def save_data(data):
    """Save data to file and session state"""
    # Create data directory if it doesn't exist
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Save to file in data directory
    file_path = data_dir / 'datathon_participants.json'
    with open(file_path, 'w') as f:
        json.dump(data, f)
    
    # Update session state
    st.session_state['optimal_groups.json'] = data

def role_selection():
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 80px; margin-bottom: 60px;"> Group Generator</h1>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 23px; font-weight: normal; margin-bottom: 40px;">Hey there! What is your profile?</h1>
        """, 
        unsafe_allow_html=True
    )

    # Add some vertical spacing
    st.markdown("<br>", unsafe_allow_html=True)

    col1, space, col2 = st.columns([1, 0.2, 1])
    
    with col1:
        if st.button("I'm a participant 👤"):
            st.session_state.page = 'participant'
            st.rerun()
    
    with col2:
        if st.button("I'm an organizer 👥"):
            st.session_state.page = 'organizer'
            st.rerun()

def participant_view():
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 60px; margin-bottom: 50px;"> 🎯 Hackathon Group Finder - Participant View</h1>
        """, 
        unsafe_allow_html=True
    )
    
    # Add back button with the same styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Home"):
            st.session_state.page = 'role_selection'
            st.rerun()
    
    if not st.session_state.get('optimal_groups.json'):
        st.error("No groups data available. Please contact the organizers.")
        return
    
    #data = st.session_state['optimal_groups.json']
    # Participant search
    st.header("Find Your Group")
    name_search = st.text_input("Enter your name")
    if name_search:
        preference = id_preference[name_search]
        found = False
        for group in best_groups_set[preference]:
            if nom_id[name_search] in group:
                        found = True                   
                        # Display group info
                        st.subheader("Your Group Members")
                        # Create columns for each member
                        cols = st.columns(len(group))
                        for col, teammate in zip(cols, group):

                            with col:
                                st.markdown(f"### {id_nom[teammate]}")
                                st.write(f"📧 {id_email[teammate]}")
                            
        if not found:
            st.warning("Name not found. Please check your spelling or contact the organizers.")

def organizer_view():
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 60px; margin-bottom: 50px;"> 🎯 Hackathon Group Finder - Organizer View</h1>
        """, 
        unsafe_allow_html=True
    )
    
    # Add back button with the same styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Home"):
            st.session_state.page = 'role_selection'
            st.rerun()
    
    # File upload section
    st.header("Upload Participants Data")
    uploaded_file = st.file_uploader("Upload your JSON file with participants data", type=['json'])
    
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            save_data(data)
            st.success("Data successfully uploaded!")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    # Display current groups
    if st.session_state.get('optimal_groups.json'):
        data = st.session_state['optimal_groups.json']
        st.header("Current Groups")
        
        # Add search/filter options
        search_option = st.selectbox(
            "Select view option",
            ["All Groups", "Search by Skill", "Group Statistics"]
        )
        
        if search_option == "All Groups":
            cols = st.columns(3)
            for idx, group in enumerate(data['groups']):
                with cols[idx % 3]:
                    with st.expander(f"Group {idx + 1}"):
                        st.write("Members:")
                        for member in group['members']:
                            st.write(f"""
                            - **{member['name']}**
                                - Email: {member['contact']}
                                - Programming: {member['skills']['programming']}/5
                                - Design: {member['skills']['design']}/5
                                - Teamwork: {member['skills']['teamwork']}/5
                            """)
                        
                        # Calculate and display group averages
                        prog_avg = sum(m['skills']['programming'] for m in group['members']) / len(group['members'])
                        design_avg = sum(m['skills']['design'] for m in group['members']) / len(group['members'])
                        team_avg = sum(m['skills']['teamwork'] for m in group['members']) / len(group['members'])
                        
                        # Create radar chart for group skills
                        fig = go.Figure()
                        fig.add_trace(go.Scatterpolar(
                            r=[prog_avg, design_avg, team_avg],
                            theta=['Programming', 'Design', 'Teamwork'],
                            fill='toself',
                            name='Group Average'
                        ))
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                            showlegend=False,
                            height=300
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        elif search_option == "Search by Skill":
            skill = st.selectbox("Select skill to analyze", ["programming", "design", "teamwork"])
            threshold = st.slider("Minimum skill level", 1, 5, 3)
            
            matching_groups = []
            for idx, group in enumerate(data['groups']):
                avg_skill = sum(m['skills'][skill] for m in group['members']) / len(group['members'])
                if avg_skill >= threshold:
                    matching_groups.append((idx, group, avg_skill))
            
            if matching_groups:
                st.write(f"Found {len(matching_groups)} groups with average {skill} skill ≥ {threshold}")
                for idx, group, avg_skill in matching_groups:
                    with st.expander(f"Group {idx + 1} (Avg {skill}: {avg_skill:.1f})"):
                        for member in group['members']:
                            st.write(f"- {member['name']} ({skill}: {member['skills'][skill]}/5)")
            else:
                st.warning("No groups found matching the criteria")
        
        else:  # Group Statistics
            st.subheader("Group Statistics")
            
            # Prepare data for visualization
            all_skills = {
                'programming': [],
                'design': [],
                'teamwork': []
            }
            
            for group in data['groups']:
                for skill in all_skills.keys():
                    avg = sum(m['skills'][skill] for m in group['members']) / len(group['members'])
                    all_skills[skill].append(avg)
            
            # Create box plots
            fig = go.Figure()
            for skill, values in all_skills.items():
                fig.add_trace(go.Box(
                    y=values,
                    name=skill.capitalize(),
                    boxpoints='all'
                ))
            
            fig.update_layout(
                title="Distribution of Skills Across Groups",
                yaxis_title="Skill Level",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data uploaded yet. Please upload a JSON file with participants data.")

def main():
    # Initialize session state
    initialize_session_state()
    
    # Route to appropriate page
    if st.session_state.page == 'role_selection':
        role_selection()
    elif st.session_state.page == 'organizer':
        organizer_view()
    elif st.session_state.page == 'participant':
        participant_view()

if __name__ == "__main__":
    main()