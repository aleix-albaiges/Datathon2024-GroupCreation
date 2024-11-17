import streamlit as st
import pandas as pd
from pathlib import Path
from script1 import process_script1
from script2 import process_script2
from script3 import process_script3
import io


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
    """Save uploaded file to data directory"""
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    file_path = data_dir / uploaded_file.name
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def convert_df_to_csv(df):
    """Convert dataframe to CSV for download"""
    return df.to_csv(index=False)

def convert_df_to_excel(df):
    """Convert dataframe to Excel for download"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


def process_dataset(df):
    """Execute all three scripts on the dataset"""
    results = {}
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Execute Script 1
        status_text.text("Processing Script 1...")
        results['script1'] = process_script1(df)
        progress_bar.progress(33)
        
        # Execute Script 2
        status_text.text("Processing Script 2...")
        results['script2'] = process_script2(df)
        progress_bar.progress(66)
        
        # Execute Script 3
        status_text.text("Processing Script 3...")
        results['script3'] = process_script3(df)
        progress_bar.progress(100)
        
        status_text.text("Processing completed!")
        
    except Exception as e:
        st.error(f"Error during processing: {str(e)}")
        return None
        
    return results

def display_results_with_download(results, original_filename):
    """Display results and provide download options"""
    if not results:
        return
    
    # Get filename without extension
    base_filename = Path(original_filename).stem
    
    # Create three columns for results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Script 1 Results")
        if isinstance(results['script1'], pd.DataFrame):
            st.dataframe(results['script1'].head())
            
            # Download buttons for Script 1 results
            st.markdown("### Download Script 1 Results")
            csv1 = convert_df_to_csv(results['script1'])
            excel1 = convert_df_to_excel(results['script1'])
            
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                st.download_button(
                    label="Download CSV",
                    data=csv1,
                    file_name=f'{base_filename}_script1_results.csv',
                    mime='text/csv',
                )
            with col1_2:
                st.download_button(
                    label="Download Excel",
                    data=excel1,
                    file_name=f'{base_filename}_script1_results.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )
    
    with col2:
        st.subheader("Script 2 Results")
        if isinstance(results['script2'], pd.DataFrame):
            st.dataframe(results['script2'].head())
            
            # Download buttons for Script 2 results
            st.markdown("### Download Script 2 Results")
            csv2 = convert_df_to_csv(results['script2'])
            excel2 = convert_df_to_excel(results['script2'])
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.download_button(
                    label="Download CSV",
                    data=csv2,
                    file_name=f'{base_filename}_script2_results.csv',
                    mime='text/csv',
                )
            with col2_2:
                st.download_button(
                    label="Download Excel",
                    data=excel2,
                    file_name=f'{base_filename}_script2_results.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )
    
    with col3:
        st.subheader("Script 3 Results")
        if isinstance(results['script3'], pd.DataFrame):
            st.dataframe(results['script3'].head())
            
            # Download buttons for Script 3 results
            st.markdown("### Download Script 3 Results")
            csv3 = convert_df_to_csv(results['script3'])
            excel3 = convert_df_to_excel(results['script3'])
            
            col3_1, col3_2 = st.columns(2)
            with col3_1:
                st.download_button(
                    label="Download CSV",
                    data=csv3,
                    file_name=f'{base_filename}_script3_results.csv',
                    mime='text/csv',
                )
            with col3_2:
                st.download_button(
                    label="Download Excel",
                    data=excel3,
                    file_name=f'{base_filename}_script3_results.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )

def main():
    st.title("Data Processing Application")
    
    # File upload section
    
if __name__ == "__main__":
    main()