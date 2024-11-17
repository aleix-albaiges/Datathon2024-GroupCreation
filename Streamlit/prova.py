import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

class Participant:
    def __init__(self, id, university, interests, preferred_role, friend_registration, preferred_team_size, availability,
                 programming_skills, interest_in_challenges, experience, languages_ordered, maturity, Tryhard, Rookie, Learner, Portfolio):
        self.id = id
        self.university = university
        self.interests = interests
        self.preferred_role = preferred_role
        self.friend_registration = friend_registration
        self.preferred_team_size = preferred_team_size
        self.availability = availability
        self.programming_skills = programming_skills
        self.interest_in_challenges = interest_in_challenges
        self.experience = experience
        self.languages_ordered = languages_ordered
        self.maturity = maturity
        self.Tryhard = Tryhard
        self.Rookie = Rookie
        self.Learner = Learner
        self.Portfolio = Portfolio



def initialize_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'role_selection'
    if 'groups_data' not in st.session_state:
        # Aquí pots inicialitzar amb un llistat de llistes d'identificadors
        st.session_state['groups_data'] = [
            ['id_participant1', 'id_participant2'],  # Grup 1
            ['id_participant3', 'id_participant4'],  # Grup 2
            # Afegeix més grups si cal
        ]

def save_data(data):
    """Save data to file and session state"""
    with open('groups_data.json', 'w') as f:
        json.dump(data, f)
    st.session_state['groups_data.json'] = data

def role_selection():
    st.title("🎯 Hackathon Groups Portal")
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.write("### Welcome! Please select your role:")
        
        # Create two big, styled buttons
        col_participant, col_organizer = st.columns(2)
        
        with col_participant:
            if st.button("👥 I'm a Participant", use_container_width=True):
                st.session_state.page = 'participant'
                st.rerun()
        
        with col_organizer:
            if st.button("🎯 I'm an Organizer", use_container_width=True):
                st.session_state.page = 'organizer'
                st.rerun()
def get_participant_data(id: str) -> Participant:
    pass
def organizer_view():
    st.title("🎯 Hackathon Group Management - Organizer View")

    if st.button("← Back to Role Selection"):
        st.session_state.page = 'role_selection'
        st.rerun()

    # Mostra els grups actuals a partir dels identificadors
    if st.session_state.get('groups_data'):
        groups = st.session_state['groups_data']
        st.header("Current Groups")

        for idx, group in enumerate(groups):
            st.write(f"### Group {idx + 1}")
            st.write("**Members:**")
            for member_id in group:
                member = get_participant_data(member_id)
                if member:
                    st.write(f"- **{member.university}**, Role: {member.preferred_role}")
                    st.write(f"  - Programming Skills: {member.programming_skills}")
                    st.write(f"  - Experience: {member.experience:.2f}")
                else:
                    st.warning(f"Participant with ID {member_id} not found.")
    else:
        st.info("No groups data available.")

def participant_view():
    st.title("🎯 Hackathon Group Finder - Participant View")
    
    # Add back button
    if st.button("← Back to Role Selection"):
        st.session_state.page = 'role_selection'
        st.rerun()
    
    if not st.session_state.get('groups_data.json'):
        st.error("No groups data available. Please contact the organizers.")
        return
    
    data = st.session_state['groups_data.json']
    
    # Participant search
    st.header("Find Your Group")
    name_search = st.text_input("Enter your name").strip().lower()
    
    if name_search:
        found = False
        for idx, group in enumerate(data['groups']):
            for member in group['members']:
                if member['name'].lower() == name_search:
                    found = True
                    st.success(f"Found you in Group {idx + 1}!")
                    
                    # Display group info
                    st.subheader("Your Group Members")
                    
                    # Create columns for each member
                    cols = st.columns(len(group['members']))
                    for col, teammate in zip(cols, group['members']):
                        with col:
                            st.markdown(f"### {teammate['name']}")
                            st.write(f"📧 {teammate['contact']}")
                            st.write("Skills:")
                            st.write(f"💻 Programming: {teammate['skills']['programming']}/5")
                            st.write(f"🎨 Design: {teammate['skills']['design']}/5")
                            st.write(f"👥 Teamwork: {teammate['skills']['teamwork']}/5")
                    
                    # Group skills visualization
                    st.subheader("Group Skills Overview")
                    fig = go.Figure()
                    
                    # Add trace for each member
                    for member in group['members']:
                        fig.add_trace(go.Scatterpolar(
                            r=[member['skills']['programming'], 
                               member['skills']['design'], 
                               member['skills']['teamwork']],
                            theta=['Programming', 'Design', 'Teamwork'],
                            fill='toself',
                            name=member['name']
                        ))
                    
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig)
                    break
        
        if not found:
            st.warning("Name not found. Please check your spelling or contact the organizers.")

def main():
    st.set_page_config(page_title="Hackathon Groups Portal", layout="wide")
    
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