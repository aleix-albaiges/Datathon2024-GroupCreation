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
class Participant2:
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

    interest_in_challenges: List[str]
    preferred_languages: List[str]
    friend_registration: List[uuid.UUID]
    preferred_team_size: int
    availability: Dict[str, bool]

    # Description of the participant
    Tryhard: float = 0
    Learner: float = 0
    Rookie: float = 0
    Portfolio: float = 0
    Experience : float = 0


def norm(d: list[tuple[str, float]]) -> float:
    '''
    Computes de Norm of the frequencies vector
    '''
    return np.sqrt(sum([freq*freq for _, freq in d]))


def normalize(d1: list[tuple[str, float]]):
    '''
    Normalize the frequencies vector
    '''
    normm = norm(d1)
    return [(k, v/normm) for k, v in d1]

def stemmer(query: str) -> str:
    '''
    Stem queries 
    '''
    res = ind.analyze(body={'analyzer':'default', 'text': query})
    query_stemmed = ''
    first = True
    for r in res['tokens']:
        if not first:
            query_stemmed += ' ' + r['token']
        else:
            query_stemmed += r['token']
            first = False
    return query_stemmed


def tf_idf():
    '''
    Compute the tfidf weights of documents terms and then compute the similarities between queries and documents.
    '''
    client = Elasticsearch("http://localhost:9200", request_timeout=1000)
    index_names = ['technical_ind', 'objective_ind']
    corpuses = {'technical_ind':{}, 'objective_ind':{}}
    
    for index_name in index_names:
        ndocs = int(client.cat.count(index=index_name, format = "json")[0]['count'])
        print(f"There are {ndocs} documents in the index '{index_name}'")


        corpus = corpuses[index_name]    # will store _normalized_ tfidf for each document, key is internal elasticsearch id, value is dictionary of term -> tf-idf weight
        for s in tqdm.tqdm(scan(client, index=index_name, query={"query" : {"match_all": {}}}), total=ndocs):
            terms = []
            freqs = []
            dfs = []

            tv = client.termvectors(index=index_name, id=s['_id'], fields=['text'], term_statistics=True, positions=False)
            if 'text' in tv['term_vectors']:   # just in case some document has no field named 'text'
                for t in tv['term_vectors']['text']['terms']:
                    f = tv['term_vectors']['text']['terms'][t]['term_freq']

                    terms.append(t)
                    freqs.append(tv['term_vectors']['text']['terms'][t]['term_freq'])
                    dfs.append(tv['term_vectors']['text']['terms'][t]['doc_freq'])

            # vector computations for tf-idf; l2-normalized for further calculations..
            tfidf = np.array(freqs) * np.log2(ndocs / np.array(dfs))
            tfidf /= np.linalg.norm(tfidf)

            # save in corpus dictionary
            corpus[s['_source']['path']] = {t: tfidf[j] for j, t in enumerate(terms)}


    #Objective_ind similarities------------------------------------------------
    r = 10  # only return r top docs
    queries = ['win prize many top dive trophy limit victory','learn skills dive improve gain experience', 'first try begin people knowledge start','level experiment journey collaborate experience']
    sims_ob : dict[str, dict[int,float]] = {}

    l2query  = [np.sqrt(len(query.split())) for query in queries]  # l2 of query assuming 0-1 vector representation

    # get nr. of docs; just for the progress bar
    ndocs = int(client.cat.count(index='objective_ind', format = "json")[0]['count'])

    # scan through docs, compute cosine sim between query and each doc
    for s in tqdm.tqdm(scan(client, index='objective_ind', query={"query" : {"match_all": {}}}), total=ndocs):
        
        docid = s['_source']['path']   # use path as id
        weights = corpuses['objective_ind'][docid]   # gets weights as a python dict of term -> weight (see remark above)
        docid = docid.split('/')[-1].replace('.txt', '')
        sims_ob[docid] = {}
        for i in range(len(queries)):
            sims_ob[docid][i] = 0.0
            for w in queries[i].split():  # gets terms as a list
                if w in weights:    # probably need to do something fancier to make sure that word is in vocabulary etc.
                    sims_ob[docid][i] += weights[w]   # accumulates if w in current doc
            # normalize sim
            sims_ob[docid][i] /= l2query[i]
    #-------------------------------------------------------------------------

    #Technical_ind similarities---------------------------------------------------------
    r = 10  # only return r top docs
    query = 'python react postgreSQL figma c++ java react pytorch sql html/css mongodb google flutter amazon raspberry tensorflow ar/vr'
    sims_technical : dict[str, float] = {}

    l2query  = np.sqrt(len(query.split()))  # l2 of query assuming 0-1 vector representation

    # get nr. of docs; just for the progress bar
    ndocs = int(client.cat.count(index='technical_ind', format = "json")[0]['count'])

    # scan through docs, compute cosine sim between query and each doc
    for s in tqdm.tqdm(scan(client, index='technical_ind', query={"query" : {"match_all": {}}}), total=ndocs):
        docid = s['_source']['path']   # use path as id
        
        weights = corpuses['technical_ind'][docid]   # gets weights as a python dict of term -> weight (see remark above)
        docid = docid.split('/')[-1].replace('.txt', '')
        sims_technical[docid] = 0.0

        for w in query.split():  # gets terms as a list
            if w in weights:    # probably need to do something fancier to make sure that word is in vocabulary etc.
                    
                sims_technical[docid] += weights[w]   # accumulates if w in current doc
            # normalize sim
        sims_technical[docid] /= l2query
    #----------------------------------------------------------------------------------------
    sims = [sims_ob, sims_technical]
    return sims


def load_participants_2(path: str, sims_ob: dict[uuid.UUID, list[float]], sims_technical: dict[uuid.UUID, list[float]]) -> list[Participant2]:
    '''
    Reload a list of new classes with the new variables and without the useless variables 
    '''
    if not pathlib.Path(path).exists():
        raise FileNotFoundError(
            f"The file {path} does not exist, are you sure you're using the correct path?"
        )
    if not pathlib.Path(path).suffix == ".json":
        raise ValueError(
            f"The file {path} is not a JSON file, are you sure you're using the correct file?"
        )

    participants_data = json.load(open(path))
    participants = []
    
    for participant_data in participants_data:
        # Remove fields that aren't in the Participant class
        if 'objective' in participant_data:
            del participant_data['objective']
        if 'introduction' in participant_data:
            del participant_data['introduction']
        if 'fun_fact' in participant_data:
            del participant_data['fun_fact']
        if 'future_excitement' in participant_data:
            del participant_data['future_excitement']
        if 'technical_project' in participant_data:
            del participant_data['technical_project']
            
        # Convert the ID string to UUID
        participant_id = str(participant_data['id'])
        
        # If this participant has simulation data, update their values
        if participant_id in sims_ob.keys():
            participant_data['Tryhard'] = sims_ob[participant_id][0]
            participant_data['Learner'] = sims_ob[participant_id][1]
            participant_data['Rookie'] = sims_ob[participant_id][2]
            participant_data['Portfolio'] = sims_ob[participant_id][3]
            participant_data['Experience'] = sims_technical[participant_id]
          
        # Create the participant instance with the updated data
        participants.append(Participant2(**participant_data))
    
    return participants


def participants_to_csv(participants: List[Participant2], output_file: str):
    """Convert list of Participant objects to CSV file."""
    # Get all fields from the first participant
    fieldnames = [field for field in vars(participants[0])]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(fieldnames)
        
        # Write each participant's data
        for participant in participants:
            row = []
            for field in fieldnames:
                value = getattr(participant, field)
                # Convert complex types to strings
                if isinstance(value, (dict, list)):
                    value = str(value)
                row.append(value)
            writer.writerow(row)    


def main() -> None:
    sims_def = tf_idf()
    participants1 = load_participants_2('data/datathon_participants.json', sims_def[0], sims_def[1])
    participants_to_csv(participants1, 'data/df_text_processed.csv')


if __name__ == '__main__':
    main()