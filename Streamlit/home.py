# Import statements
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

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
    if 'groups_data.json' not in st.session_state:
        if Path('groups_data.json').exists():
            with open('groups_data.json', 'r') as f:
                st.session_state['groups_data.json'] = json.load(f)
        else:
            st.session_state['groups_data.json'] = None

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
    st.session_state['groups_data.json'] = data

def role_selection():
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 60px; margin-bottom: 50px;"> Group Generator</h1>
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
    st.header("Upload Groups Data")
    uploaded_file = st.file_uploader("Upload your JSON file with groups data", type=['json'])
    
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            save_data(data)
            st.success("Data successfully uploaded!")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    # Display current groups
    if st.session_state.get('groups_data.json'):
        data = st.session_state['groups_data.json']
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
        st.info("No data uploaded yet. Please upload a JSON file with groups data.")

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