import subprocess 

directories = ['/Users/cristinateixidocruilles/Desktop/Datathon24/Similarities/Objective_files', '/Users/cristinateixidocruilles/Desktop/Datathon24/Similarities/Technical_files']
index_names = ['objective_ind', 'technical_ind']

def index_documents(script_path, index_name, extract_dir):
    print("Indexing documents...")
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

path = input("Please enter the file or directory path where you have IndexFilesPreprocess.py: ")
script_path = path

for i in range(2):
    EXTRACT_DIR = directories[i]
    INDEX_NAME = index_names[i]
    index_documents(script_path, INDEX_NAME, EXTRACT_DIR)
