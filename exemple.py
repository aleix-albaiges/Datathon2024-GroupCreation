from participant import load_participants
from rich import print
import pandas as pd

data_path = "data/datathon_participants.json"
participants = load_participants(data_path)

df = pd.read_json("camí/del/teu/arxiu.json")