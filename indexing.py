import subprocess  # Import subprocess

directories = ['Objectives_files', 'Technical_files']
index_names = ['objective_ind', 'technical_ind']



def index_documents(script_path, index_name, extract_dir):
    print("Indexing documents...")
    # Construct the command to run IndexFilesPreprocess.py
    command = [
        'python3', script_path,
        '--index', index_name,
        '--path', extract_dir,
        '--token', 'letter',
        '--filter', 'lowercase', 'asciifolding', 'stop', 'porter_stem'
    ]
    # Execute the script with the specified arguments
    subprocess.run(command)
    print("Indexing completed.")

script_path = 'IndexFilesPreprocess.py'  # Make sure this path is correct

for i in range(2):
    EXTRACT_DIR = directories[i]
    INDEX_NAME = index_names[i]
    index_documents(script_path, INDEX_NAME, EXTRACT_DIR)
