import json
import pathlib
import uuid
from dataclasses import dataclass
import os
from typing import Dict, List, Literal
import subprocess
import tqdm
import numpy as np
import pickle
from rich import print
import heapq
from pprint import pprint
from collections import Counter, defaultdict
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch_dsl import Search, Index, analyzer, tokenizer
from elasticsearch_dsl.query import Q
import csv



@dataclass
class Participant:
    id: uuid.UUID  # Unique identifier

    # Personal data
    name: str
    email: str
    age: int
    year_of_study: Literal["1st year", "2nd year", "3rd year", "4th year", "Masters", "PhD"]
    shirt_size: Literal["S", "M", "L", "XL"]
    university: str
    dietary_restrictions: Literal["None", "Vegetarian", "Vegan", "Gluten-free", "Other"]

    # Experience and programming skills
    programming_skills: Dict[str, int]
    experience_level: Literal["Beginner", "Intermediate", "Advanced"]
    hackathons_done: int

    # Interests, preferences and constraints
    interests: List[str]
    preferred_role: Literal[
        "Analysis", "Visualization", "Development", "Design", "Don't know", "Don't care"
    ]
    objective: str
    interest_in_challenges: List[str]
    preferred_languages: List[str]
    friend_registration: List[uuid.UUID]
    preferred_team_size: int
    availability: Dict[str, bool]

    # Description of the participant
    introduction: str
    technical_project: str
    future_excitement: str
    fun_fact: str



def load_participants(path: str) -> List[Participant]:
    if not pathlib.Path(path).exists():
        raise FileNotFoundError(
            f"The file {path} does not exist, are you sure you're using the correct path?"
        )
    if not pathlib.Path(path).suffix == ".json":
        raise ValueError(
            f"The file {path} is not a JSON file, are you sure you're using the correct file?"
        )

    return [Participant(**participant) for participant in json.load(open(path))]


def sims(path_json_participants: str = 'data/datathon_participants.json') -> None:
    
    participants = load_participants(path_json_participants)
    objectives : dict[uuid.UUID,str] = {}
    technical : dict[uuid.UUID,str] = {}

    for p in participants:
        objectives[p.id] = p.objective + " " + p.introduction
        technical[p.id] = p.technical_project + " " + p.future_excitement
    
    #Technical files
    nom_carpeta_technical = "technical_files_dir"
    os.makedirs(nom_carpeta_technical, exist_ok=True)

    for clau, valor in technical.items():
        nom_fitxer = f"{clau}.txt"  # Nom del fitxer
        ruta_fitxer = os.path.join(nom_carpeta_technical, nom_fitxer)
    
        with open(ruta_fitxer, "w", encoding="utf-8") as fitxer:
            fitxer.write(valor)
    
    #Objectives files
    nom_carpeta_objectives = "objective_files_dir"
    os.makedirs(nom_carpeta_objectives, exist_ok=True)

    for clau, valor in objectives.items():
        nom_fitxer = f"{clau}.txt"  # Nom del fitxer
        ruta_fitxer = os.path.join(nom_carpeta_objectives, nom_fitxer)
        
        with open(ruta_fitxer, "w", encoding="utf-8") as fitxer:
            fitxer.write(valor)


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


def indexing(path_to_file_IndexfilesPreprocess: str) -> None:
    directories = ['objective_files_dir', 'technical_files_dir']
    index_names = ['objective_ind', 'technical_ind']

    for i in range(2):
        EXTRACT_DIR = directories[i]
        INDEX_NAME = index_names[i]
        index_documents(path_to_file_IndexfilesPreprocess, INDEX_NAME, EXTRACT_DIR)


def main() -> None:
    sims()
    indexing('D:\Github\Datathon2024-GroupCreation\Similarities\IndexFilesPreprocess.py')

   

if __name__ == '__main__':
    main()


