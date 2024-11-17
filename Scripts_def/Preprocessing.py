from participant import load_participants
from rich import print
import pandas as pd
import numpy as np


def preprocessing(path_json_participants: str = 'data/datathon_participants.json', path_df_text_processed: str = 'data/df_text_processed.csv', path_final_preprocessed_df: str = 'data/data_preprocessed.csv') -> None:
    '''
    path_json_participants: str -> path of raw json data of participants.
    path_df_text_processed: str -> path of output text_processing.py. 
    path_final_preprocessed_df: str -> path to load the final preprocessed dataset.

    Transforms the dataset to a new one cleaned and properly modificated to use in next steps (distance_calculation.py, clustering_optimization.py)
    '''
    #read and convert json to pd.Dateframe
    print('Reading json and converting to df...')
    df: pd.DataFrame = pd.read_json(path_json_participants)
    print('Readed')

    #drop useless variables
    print('Dropping Useless columns...')
    df.drop(['name', 'email', 'shirt_size', 'dietary_restrictions', 'objective', 'introduction','fun_fact', 'future_excitement', 'technical_project'], axis=1, inplace=True)
    print('Dropped')

    #Preprocessing variables
    print('Preprocessing some variables...')
    mapping_year_of_study = {'1st year': 1,'2nd year': 2,'3rd year': 3,'4th year': 4,'Masters': 5,'PhD': 6}
    df['year_of_study'] = df['year_of_study'].map(mapping_year_of_study)

    all_interests = df['interests'].explode().unique()
    for value in all_interests: df[f'has_{value}'] = df['interests'].apply(lambda x: 1 if value in x else 0)
    df['interests'] = df[[f'has_{value}' for value in all_interests]].values.tolist()
    df = df.drop(columns=[f'has_{value}' for value in all_interests])

    mapping_experience_level = {'Advanced': 10,'Intermediate': 4, 'Beginner': 1}
    df['experience_level'] = df['experience_level'].map(mapping_experience_level)
    df['experience'] = df['experience_level'] * np.log(1 + df['hackathons_done'])
    df.drop(['experience_level', 'hackathons_done'], axis=1, inplace=True)

    def sort_languages(languages):
        preference_order = {'Catalan': 0,'Spanish': 1,'English': 2}
        def sort_key(language): return preference_order.get(language, 3)
        return sorted(languages, key=sort_key)
    df['languages_ordered'] = df['preferred_languages'].apply(sort_languages)
    df.drop('preferred_languages', axis=1, inplace=True)

    weight_level, weight_age = 1, 0.2
    df['maturity'] = (df['year_of_study'] * weight_level) + ((df['age'] - 18) * weight_age)
    df.drop(['age', 'year_of_study'], axis=1, inplace=True)

    time_slots_order = ['Saturday morning', 'Saturday afternoon', 'Saturday night', 'Sunday morning', 'Sunday afternoon']
    def time_slots_to_vector(time_slots): return [1 if time_slots.get(slot, False) else 0 for slot in time_slots_order]
    df['availability'] = df['availability'].apply(time_slots_to_vector)
    print('Preprocessed')

    #Merge the two preprocessed datasets to obtain de final preprocessed dataset
    print('Merging datasets...')
    common_identifier, columns_to_add = "id", ["Tryhard", "Rookie", "Learner", "Portfolio"]
    df1 = pd.read_csv(path_df_text_processed)
    df_merged = pd.merge(df, df1[[common_identifier] + columns_to_add], on=common_identifier, how="left")
    df_merged.to_csv(path_final_preprocessed_df, index=False)
    print('Merged and Loaded :)')



