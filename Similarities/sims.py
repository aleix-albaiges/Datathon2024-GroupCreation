import json
import pathlib
import uuid
from dataclasses import dataclass
import os
from typing import Dict, List, Literal


from dataclasses import dataclass
from typing import Dict, List, Literal
import uuid

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


data_path = "/Users/cristinateixidocruilles/Desktop/Datathon24/Similarities/data/datathon_participants.json"
participants = load_participants(data_path)

objectives : dict[uuid.UUID,str] = {}

technical : dict[uuid.UUID,str] = {}


for p in participants:
    objectives[p.id] = p.objective + " " + p.introduction
    technical[p.id] = p.technical_project + " " + p.future_excitement


# Ruta al teu escriptori
path = input("Please enter the file or directory path where you want to download the files: ")
ruta_base = path
nom_carpeta = "Technical_files"
ruta_carpeta = os.path.join(ruta_base, nom_carpeta)
# Crear la carpeta si no existeix
os.makedirs(ruta_carpeta, exist_ok=True)

# Crear els fitxers
for clau, valor in technical.items():
    nom_fitxer = f"{clau}.txt"  # Nom del fitxer
    ruta_fitxer = os.path.join(ruta_carpeta, nom_fitxer)
    
    # Escriure el contingut al fitxer
    with open(ruta_fitxer, "w", encoding="utf-8") as fitxer:
        fitxer.write(valor)


ruta_base = path
nom_carpeta = "Objective_files"
ruta_carpeta = os.path.join(ruta_base, nom_carpeta)
# Crear la carpeta si no existeix
os.makedirs(ruta_carpeta, exist_ok=True)

# Crear els fitxers
for clau, valor in objectives.items():
    nom_fitxer = f"{clau}.txt"  # Nom del fitxer
    ruta_fitxer = os.path.join(ruta_carpeta, nom_fitxer)
    
    # Escriure el contingut al fitxer
    with open(ruta_fitxer, "w", encoding="utf-8") as fitxer:
        fitxer.write(valor)

print(f"Fitxers creats a la carpeta: {ruta_carpeta}")