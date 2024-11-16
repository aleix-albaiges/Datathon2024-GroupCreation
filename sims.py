from participant import load_participants
from rich import print
import uuid
import os


data_path = "data/datathon_participants.json"
participants = load_participants(data_path)

objectives : dict[uuid.UUID,str] = {}

technical : dict[uuid.UUID,str] = {}


for p in participants:
    objectives[p.id] = p.objective + " " + p.introduction
    technical[p.id] = p.technical_project + " " + p.future_excitement

    
print(objectives[participants[0].id])
print(1)
print(technical[participants[0].id])

# Ruta al teu escriptori
ruta_base = r"C:\Users\fortu\Documents\GitHub\Datathon2024-GroupCreation"
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

print(f"Fitxers creats a la carpeta: {ruta_carpeta}")

