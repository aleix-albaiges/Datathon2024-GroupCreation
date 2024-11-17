from rich import print
import pandas as pd
import numpy as np
import math
import ast
from dataclasses import dataclass
from collections import defaultdict
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
import random
from itertools import combinations
import json
from participant import load_participants
import pickle
from prettytable import PrettyTable


@dataclass
class Participant_scores:
    def __init__(self, id : str, university : str, interests : list[int], preferred_role : str, friend_registration : list[str], 
                 preferred_team_size : int, availability : list[int],
                 programming_skills : dict[str, int], interest_in_challenges : list[str], experience : float, 
                 languages_ordered : list[str], maturity : float, Tryhard : float, 
                 Rookie : float, Learner : float, Portfolio : float):
        self.id = id
        self.university = university
        self.interests = interests
        self.preferred_role = preferred_role
        self.friend_registration = friend_registration
        self.preferred_team_size = preferred_team_size
        self.availability = availability
        self.programming_skills = programming_skills
        self.interest_in_challenges = interest_in_challenges
        self.experience = experience
        self.languages_ordered = languages_ordered
        self.maturity = maturity
        self.Tryhard = Tryhard
        self.Rookie = Rookie
        self.Learner = Learner
        self.Portfolio = Portfolio


def dist_university(university_1:str, university_2:str) :
    if university_1 == university_2:
        return 0 
    else:
        return 10
    

def dist_friends(friend_registration_1:list[str], friend_registration_2:list[str], id_1:str, id_2:str):
    if id_1 in friend_registration_2 and id_2 in friend_registration_1:
        return 0
    elif id_1 in friend_registration_2 or id_2 in friend_registration_1:
        return 1
    return 10


def dist_one_hot_encoding(x, y) -> float:
    return sum([1 if x_i != y_i else 0 for x_i, y_i in zip(x, y)])


def dist_programming_skills(skills_1:dict[str,int], skills_2:dict[str,int]) -> float:
    avg_level_1 = sum(skills_1.values()) / len(skills_1) if skills_1 else 0
    
    avg_level_2 = sum(skills_2.values()) / len(skills_2) if skills_2 else 0
    
    distance_avg_levels = abs(avg_level_1 - avg_level_2)
    
    all_skills = set(skills_1.keys()).union(set(skills_2.keys()))
    
    distance_union = 1 / len(all_skills) if all_skills else 10 
    return distance_avg_levels + distance_union


def dist_preferred_role(role_1:str, role_2:str):
    if role_1 == role_2:
        return 1.0  

    if role_1 == "Don't know" or role_2 == "Don't know":
        return 1 / 0.2  

    if role_1 == "Don't care" or role_2 == "Don't care":
        return 0.5  

    return 0.0

def dist_language(languages_1:list[str], languages_2:list[str]):
    if not languages_1 or not languages_2:  
        return 0
    
    common_languages = set(languages_1).intersection(set(languages_2))
    
    if not common_languages:  
        return 100

    for i, lang_1 in enumerate(languages_1):
        for j, lang_2 in enumerate(languages_2):
            if lang_1 == lang_2:
                d = abs(i - j)
                return d + math.exp(i+j) - 1
            

def get_min_max_values(participants_dict : dict[str,Participant_scores], weights:dict[str,float]):
    # Minimum and maximum values for each score
    min_values = {
        'university': float('inf'),
        'interests': float('inf'),
        'preferred_role': float('inf'),
        'availability': float('inf'),
        'programming_skills': float('inf'),
        'interests_in_challenges': float('inf'),
        'languages': float('inf'),
        'experience': float('inf'),
        'maturity': float('inf'),
        'profile': float('inf'),
        'friends': float('inf')
    }

    max_values = {
        'university': float('-inf'),
        'interests': float('-inf'),
        'preferred_role': float('-inf'),
        'availability': float('-inf'),
        'programming_skills': float('-inf'),
        'interests_in_challenges': float('-inf'),
        'languages': float('-inf'),
        'experience': float('-inf'),
        'maturity': float('-inf'),
        'profile': float('-inf'),
        'friends': float('-inf')
    }

    # Iterate on all the participants and calculating the 2-to-2 distances.
    participant_ids = list(participants_dict.keys())
    
    for i in range(len(participant_ids)):
        for j in range(i + 1, len(participant_ids)):  # Do not calculate the same pair twice
            p1 = participants_dict[participant_ids[i]]
            p2 = participants_dict[participant_ids[j]]
            
            
            # Calcula les distàncies per atributs individuals
            d_university = dist_university(p1.university, p2.university) 
            d_interests = dist_one_hot_encoding(p1.interests, p2.interests) 
            d_preferred_role = dist_preferred_role(p1.preferred_role, p2.preferred_role) 
            d_availability = dist_one_hot_encoding(p1.availability, p2.availability) 
            d_programming_skills = dist_programming_skills(p1.programming_skills, p2.programming_skills) 
            d_interests_in_challenges = dist_one_hot_encoding(p1.interest_in_challenges, p2.interest_in_challenges) 
            d_languages = dist_language(p1.languages_ordered, p2.languages_ordered) 
            d_experience = abs(p1.experience - p2.experience) 
            d_maturity = abs(p1.maturity - p2.maturity) 
            d_profile = (abs(p1.Tryhard - p2.Tryhard) + abs(p1.Rookie - p2.Rookie) + abs(p1.Learner - p2.Learner) + abs(p1.Portfolio - p2.Portfolio)) 
            d_friend = dist_friends(p1.friend_registration, p2.friend_registration, p1.id, p2.id) 
            
            # Actualitze min and max for each attribute
            min_values['university'] = min(min_values['university'], d_university)
            max_values['university'] = max(max_values['university'], d_university)

            min_values['interests'] = min(min_values['interests'], d_interests)
            max_values['interests'] = max(max_values['interests'], d_interests)

            min_values['preferred_role'] = min(min_values['preferred_role'], d_preferred_role)
            max_values['preferred_role'] = max(max_values['preferred_role'], d_preferred_role)

            min_values['availability'] = min(min_values['availability'], d_availability)
            max_values['availability'] = max(max_values['availability'], d_availability)

            min_values['programming_skills'] = min(min_values['programming_skills'], d_programming_skills)
            max_values['programming_skills'] = max(max_values['programming_skills'], d_programming_skills)

            min_values['interests_in_challenges'] = min(min_values['interests_in_challenges'], d_interests_in_challenges)
            max_values['interests_in_challenges'] = max(max_values['interests_in_challenges'], d_interests_in_challenges)

            min_values['languages'] = min(min_values['languages'], d_languages)
            max_values['languages'] = max(max_values['languages'], d_languages)

            min_values['experience'] = min(min_values['experience'], d_experience)
            max_values['experience'] = max(max_values['experience'], d_experience)

            min_values['maturity'] = min(min_values['maturity'], d_maturity)
            max_values['maturity'] = max(max_values['maturity'], d_maturity)

            min_values['profile'] = min(min_values['profile'], d_profile)
            max_values['profile'] = max(max_values['profile'], d_profile)

            min_values['friends'] = min(min_values['friends'], d_friend)
            max_values['friends'] = max(max_values['friends'], d_friend)

    return min_values, max_values


def combined_distance(participant1: Participant_scores, participant2: Participant_scores, weights: dict[str, float], min_values: dict[str,float], max_values: dict[str,float]) -> float:
    # Calcular les distàncies per atribut
    d_university = dist_university(participant1.university, participant2.university)
    d_interests = dist_one_hot_encoding(participant1.interests, participant2.interests)
    d_preferred_role = dist_preferred_role(participant1.preferred_role, participant2.preferred_role)
    d_availability = dist_one_hot_encoding(participant1.availability, participant2.availability)
    d_programming_skills = dist_programming_skills(participant1.programming_skills, participant2.programming_skills)
    d_interests_in_challenges = dist_one_hot_encoding(participant1.interest_in_challenges, participant2.interest_in_challenges)
    d_languages = float(dist_language(participant1.languages_ordered, participant2.languages_ordered))
    d_experience : float = abs(participant1.experience - participant2.experience)
    d_maturity = abs(participant1.maturity - participant2.maturity)
    d_profile = (abs(participant1.Tryhard - participant2.Tryhard) + abs(participant1.Rookie - participant2.Rookie) + abs(participant1.Learner - participant2.Learner) + abs(participant1.Portfolio - participant2.Portfolio))
    d_friend = dist_friends(participant1.friend_registration, participant2.friend_registration, participant1.id, participant2.id)

    # Normalitzar les distàncies utilitzant els mínims i màxims
    d_university_normalized = (d_university - min_values['university']) / (max_values['university'] - min_values['university']) if max_values['university'] > min_values['university'] else 0
    d_interests_normalized = (d_interests - min_values['interests']) / (max_values['interests'] - min_values['interests']) if max_values['interests'] > min_values['interests'] else 0
    d_preferred_role_normalized = (d_preferred_role - min_values['preferred_role']) / (max_values['preferred_role'] - min_values['preferred_role']) if max_values['preferred_role'] > min_values['preferred_role'] else 0
    d_availability_normalized = (d_availability - min_values['availability']) / (max_values['availability'] - min_values['availability']) if max_values['availability'] > min_values['availability'] else 0
    d_programming_skills_normalized = (d_programming_skills - min_values['programming_skills']) / (max_values['programming_skills'] - min_values['programming_skills']) if max_values['programming_skills'] > min_values['programming_skills'] else 0
    d_interests_in_challenges_normalized = (d_interests_in_challenges - min_values['interests_in_challenges']) / (max_values['interests_in_challenges'] - min_values['interests_in_challenges']) if max_values['interests_in_challenges'] > min_values['interests_in_challenges'] else 0
    d_languages_normalized = (d_languages - min_values['languages']) / (max_values['languages'] - min_values['languages']) if max_values['languages'] > min_values['languages'] else 0
    d_experience_normalized = (d_experience - min_values['experience']) / (max_values['experience'] - min_values['experience']) if max_values['experience'] > min_values['experience'] else 0
    d_maturity_normalized = (d_maturity - min_values['maturity']) / (max_values['maturity'] - min_values['maturity']) if max_values['maturity'] > min_values['maturity'] else 0
    d_profile_normalized = (d_profile - min_values['profile']) / (max_values['profile'] - min_values['profile']) if max_values['profile'] > min_values['profile'] else 0
    d_friend_normalized = (d_friend - min_values['friends']) / (max_values['friends'] - min_values['friends']) if max_values['friends'] > min_values['friends'] else 0

    # Multiplicar les distàncies normalitzades pels pesos corresponents
    d_university_weighted = d_university_normalized * weights['university']
    d_interests_weighted = d_interests_normalized * weights['interests']
    d_preferred_role_weighted = d_preferred_role_normalized * weights['preferred_role']
    d_availability_weighted = d_availability_normalized * weights['availability']
    d_programming_skills_weighted = d_programming_skills_normalized * weights['programming_skills']
    d_interests_in_challenges_weighted = d_interests_in_challenges_normalized * weights['interests_in_challenges']
    d_languages_weighted = d_languages_normalized * weights['languages']
    d_experience_weighted = d_experience_normalized * weights['experience']
    d_maturity_weighted = d_maturity_normalized * weights['maturity']
    d_profile_weighted = d_profile_normalized * weights['profile']
    d_friend_weighted = d_friend_normalized * weights['friends']

    # Sumar les distàncies ponderades
    total_distance = (
        d_university_weighted +
        d_interests_weighted +
        d_preferred_role_weighted +
        d_availability_weighted +
        d_programming_skills_weighted +
        d_interests_in_challenges_weighted +
        d_languages_weighted +
        d_experience_weighted +
        d_maturity_weighted +
        d_profile_weighted +
        d_friend_weighted
    )
    return total_distance


def calculate_distance_matrix(participants_dict : dict[str,Participant_scores], weights:dict[str,float], min_values:dict[str, float], max_values:dict[str, float], id_nombre: dict[str,int]) -> tuple[list[list[float]],list[str]]:
    # Llista de tots els participants
    participant_ids = list(participants_dict.keys())
    num_participants = len(participant_ids)

    # Inicialitzar la matriu de distàncies amb zeros
    distance_matrix : list[list[float]] = np.zeros((num_participants, num_participants))

    # Recorre cada parell de participants
    for i in range(num_participants):
        id_nombre[participant_ids[i]] = i
        
        for j in range(i + 1, num_participants):  # Comença a j=i+1 per evitar duplicats i càlculs innecessaris
            participant1 = participants_dict[participant_ids[i]]
            participant2 = participants_dict[participant_ids[j]]

            # Calcula la distància normalitzada
            distance = combined_distance(participant1, participant2, weights, min_values, max_values)
            
            # Omple la matriu de distàncies (simètrica)
            distance_matrix[i, j] = distance
            distance_matrix[j, i] = distance

    return distance_matrix, participant_ids



#ALGORITHM: SIMULATED ANNEALING

def loss_function(grup: list[str], matrix: list[list[float]], id_nombre: dict[str,int]) -> float:
    """
    Loss function is the sum of the distances within all the elements of a group for all the groups. All distances are positives.
    """
    return sum(matrix[id_nombre[x]][id_nombre[y]] for x,y in combinations(grup,2))

def generar_grups_aleatoris(participants:list[str],group_size:int) -> list[list[str]]:
    random.shuffle(participants)
    grups : list[list[str]] = []
    for i in range(0, len(participants), group_size):
        grups.append(participants[i:i+group_size])
    return grups

def calculate_loss(grups: list[list[str]], matrix: list[list[float]], id_nombre: dict[str,int]) -> float:
    
    return sum(loss_function(grup, matrix, id_nombre) for grup in grups)

def muta_grups_aleatoriament(grups: list[list[str]]):
    # Exemples de mútacions:
    grups_canvi = random.sample(grups, len(grups)//2)
    participants_canvi :list[str] = []
    for grup in grups_canvi:
        p = random.choice(grup)
        grup.remove(p)
        participants_canvi.append(p) 
    
    random.shuffle(participants_canvi)
    for i in range(len(grups_canvi)):
        grups_canvi[i].append(participants_canvi[i])


def simulated_annealing(participants: list[str], group_size:int, matrix: list[list[float]], id_nombre: dict[str,int], inicial_temperature:int=100, cooldown:float=0.95, max_iterations:int=4000) -> tuple[list[list[str]], float]:
    """
    Applies simulated_annealing algorithm.
    """
    best_solution = generar_grups_aleatoris(participants,group_size) # First solution
    
    best_loss = calculate_loss(best_solution, matrix, id_nombre)
    temperature = inicial_temperature
    
    for _ in range(max_iterations):
        # New solution, candidate
        new_solution = best_solution[:]
        muta_grups_aleatoriament(new_solution)
        
        # Calculate loss function of the new solution
        new_loss = calculate_loss(new_solution, matrix, id_nombre)
        
        # Determine if we accept the new solution
        if new_loss < best_loss:
            best_solution = new_solution
            best_loss = new_loss
        
        else:
            accept_prob = math.exp((best_loss - new_loss) / temperature)
            if random.random() < accept_prob:
                best_solution = new_solution
                best_loss = new_loss
        
        # cooldown
        temperature *= cooldown
    
    return best_solution, best_loss


def save_pickle(variable, path: str):
    try:
        with open(path, 'wb') as handle:
            pickle.dump(variable, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return 'ok!'
    except Exception as err:
        print("An error occurred!!!: " + str(err))

        
def load_pickle(path):
    try:
        with open(path, 'rb') as handle:
            return pickle.load(handle)
    except Exception as err:
        print("An error occurred!!!: " + str(err))
        return None



def main(weights : dict[str,float] = {'university': 0.25,'interests': 0.75,'preferred_role': 1,'availability': 0.5,'programming_skills': 2,'interests_in_challenges': 3,'languages': 4,'experience': 2.5,'maturity': 0.5,'profile': 1.5,'friends' : 6}) -> None:
    df = pd.read_csv('data/data_preprocessed.csv')

    participants_dict : dict[str, Participant_scores]= {}
    
    for _, row in df.iterrows():
        programming_skills = ast.literal_eval(row['programming_skills'])  
        interests = ast.literal_eval(row['interests']) 
        friend_registration = ast.literal_eval(row['friend_registration'])  
        availability = ast.literal_eval(row['availability'])  
        interest_in_challenges = ast.literal_eval(row['interest_in_challenges'])  
        languages_ordered = ast.literal_eval(row['languages_ordered'])  

        
        participant = Participant_scores(
            id = row['id'],
            university=row['university'],
            interests=interests,  
            preferred_role=row['preferred_role'],
            friend_registration=friend_registration,  
            preferred_team_size=row['preferred_team_size'],
            availability=availability,  
            programming_skills=programming_skills,  
            interest_in_challenges=interest_in_challenges,  
            experience=row['experience'],
            languages_ordered=languages_ordered,  
            maturity=row['maturity'],
            Tryhard=row['Tryhard'],
            Rookie=row['Rookie'],
            Learner=row['Learner'],
            Portfolio=row['Portfolio']
        )
    
        participants_dict[row['id']] = participant

    #DISTANCES
    id_nombre : dict[str,int] = {}

    min_values, max_values = get_min_max_values(participants_dict, weights)
    matrix, ids = calculate_distance_matrix(participants_dict, weights, min_values, max_values, id_nombre)


    #ALGORITHM BEST GROUPS
    participants : dict[int,list[str]] = {i:[idp for idp, participant in participants_dict.items() if participant.preferred_team_size == i] for i in range(5)}
    best_groups : dict[int,list[list[str]]] = {i : [] for i in range(5)}
    best_losses = [0.0 for _ in range(5)]
    prov_groups : dict[int,list[list[str]]] = {i : [] for i in range(5)}
    prov_losses = [0.0 for _ in range(5)]
    for k in range(10):
        for i in range(5):
            if i < 2:
                best_groups[i] = [[a] for a in participants[i]]
            else:
                prov_groups[i], prov_losses[i] = simulated_annealing(participants[i],i,matrix,id_nombre)
                if prov_losses[i] < best_losses[i] or k==0:
                    best_losses[i] = prov_losses[i]
                    best_groups[i] = prov_groups[i] 
        #print(best_losses)   

    #LOAD final groups json
    with open("best_groups.json", "w", encoding="utf-8") as json_file:
        json.dump(best_groups, json_file, ensure_ascii=False, indent=4)

    data_path = "data/datathon_participants.json"

    participants_sencer = load_participants(data_path)

    id_nom : dict[str,str] = {}

    id_email : dict[str,str] = {}

    for p in participants_sencer:

        id_nom[str(p.id)] = p.name

        id_email[str(p.id)] = p.email

    save_pickle(id_nom, "id_nom.pickle")
    save_pickle(id_email, "id_email.pickle")

    best_groups_4 = best_groups[4][:4]
    for idx, grup in enumerate(best_groups_4, start=1):
        print(f"Grup {idx}")
        taula = PrettyTable()
        taula.field_names = ["Nom", "Email"]
        
        for persona in grup:
            nom, email = id_nom[persona], id_email[persona]
            taula.add_row([nom, email])
        
        print(taula)
        print("\n" + "-" * 40 + "\n") 

if __name__ == '__main__':
    main()