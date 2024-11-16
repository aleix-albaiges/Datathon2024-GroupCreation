import subprocess 

EXTRACT_DIR = 'arxiv'
INDEX_NAME = 'exercise2'

def index_documents(script_path, index_name, extract_dir):
    print("Indexing documents...")
    # Construct the command to run IndexFilesPreprocess.py
    command = [
        'python3', script_path,
        '--index', index_name,
        '--path', extract_dir,
        '--token', 'letter',
        '--filter', 'lowercase', 'asciifolding'
    ]
    # Execute the script with the specified arguments
    subprocess.run(command)
    print("Indexing completed.")

script_path = 'IndexFilesPreprocess.py'  # Make sure this path is correct
index_documents(script_path, INDEX_NAME, EXTRACT_DIR)