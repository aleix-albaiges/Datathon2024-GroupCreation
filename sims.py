from participant import load_participants
from rich import print
import uuid

data_path = "data/datathon_participants.json"
participants = load_participants(data_path)

objectives : dict[uuid.UUID,str] = {}

for p in participants:
    objectives[p.id] = p.objective
    
print(objectives[participants[8].id])

