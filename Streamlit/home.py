import streamlit as st
import pandas as pd
from vega_datasets import data
import altair as alt

# Page configuration
st.set_page_config(
    page_title="Group generator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for page navigation
page = st.sidebar.selectbox(
    "Select page",
    ("Home", "I'm a participant", "I'm a organizer")
)

def main():
    if page == "Home":
        st.markdown(
            """
            <h1 style="text-align: center; font-size: 60px; "> Group Generator</h1>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <h1 style="text-align: center; font-size: 23px; font-weight: normal;">Hey there! What is your profile?</h1>
            """, 
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        
        # Button in the first column
        with col1:
            if st.button("I'm a participant"):
                st.switch_page("pages/participant.py")
        
        # Button in the second column
        with col2:
            if st.button("I'm an organizer"):
                st.switch_page("pages/organizer.py")

    elif page == "I'm a participant":
        st.title("I'm a participant")
        st.write("Welcome, Participant!")

    elif page == "I'm a organizer":
        st.title("I'm an organizer")
        st.write("Welcome, Organizer!")
        
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "txt"])
        
        if uploaded_file is not None:
            file_details = {
                "Filename": uploaded_file.name,
                "FileType": uploaded_file.type,
                "FileSize": uploaded_file.size
            }
            # Display file details
            st.write(file_details)
            
            if uploaded_file.type == "text/csv":
                # Read CSV
                df = pd.read_csv(uploaded_file)
                st.write(df)
    
    else:
        st.title("Main Page")
        st.write("Choose your role using the buttons above!")

if __name__ == "__main__":
    main()