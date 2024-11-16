from elasticsearch.helpers import scan
import tqdm
import numpy as np
import pickle

from elasticsearch import Elasticsearch
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
        corpus[s['_id']] = {t: tfidf[j] for j, t in enumerate(terms)}

