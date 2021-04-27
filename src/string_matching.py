
import pandas as pd
from collections import Counter
from src import common


def name_similarity(name_a, name_b, token_frequency):
    """"""
    
    a_tokens = set(name_a)
    b_tokens = set(name_b)
    a_uniq = sequence_uniqueness(name_a, token_frequency)
    b_uniq = sequence_uniqueness(name_b, token_frequency)
    if a_uniq == 0 or b_uniq == 0:
        return 0
    else:
        return sequence_uniqueness(a_tokens.intersection(b_tokens), token_frequency) / (a_uniq * b_uniq) ** 0.5

    
def build_token_frequency_table(token_lists):
    """"""
    
    tokens = [str(token) for s in token_lists for token in s]
    return Counter(tokens)



def match_firm_hash(dfbase, dfmatch, min_score=0.5, verbose=True):
    """"""

    base_firm_names = list(dfbase['firm'].values)
    base_firm_hashed = list(dfbase['firmhash'].values)

    firm_hash_dict = {}
    for bn, bh in zip(base_firm_names, base_firm_hashed):
        firm_hash_dict[bn] = {
            'hash': bh,
            'tokens': common.to_clean_tokens(bn)
        }

    match_firm_names = list(dfmatch['firm'].values)
    match_firms_tokenized = [common.to_clean_tokens(f) for f in match_firm_names]
    match_firm_dict = {}
    for mn, mt in zip(match_firm_names, match_firms_tokenized):
        match_firm_dict[mn] = {
            'tokens': mt,
        }

    all_companies_tokenized = [*[v['tokens'] for v in firm_hash_dict.values()], *match_firms_tokenized]

    token_frequency = build_token_frequency_table(all_companies_tokenized)
    
    no_match = 0
    for mk, mv in match_firm_dict.items():
        match_scores = []
        max_score = 0
        best_match = None
        for bk, bv in firm_hash_dict.items():
            try:
                subscore = name_similarity(bv['tokens'], mv['tokens'], token_frequency)
            except:
                subscore = 0
                print('Error on similarity match')
                print(bv['tokens'])
                print(mk)
            if subscore > min_score:
                if subscore > max_score:
                    max_score = subscore
                    best_match = bv['hash']
        match_firm_dict[mk]['hash'] = best_match
        match_firm_dict[mk]['match_score'] = max_score
        if max_score <= min_score:
            no_match += 1
            if verbose:
                print(f'No match found for: {mk}')

    df_hashmatch = pd.DataFrame({
        'firm': match_firm_dict.keys(),
        'firmhash': [v['hash'] for v in match_firm_dict.values()]
    })
    df_hashmatch['firmhash'] = df_hashmatch['firmhash'].fillna(0).astype(int)

    dfmatch = dfmatch.merge(df_hashmatch, on='firm', how='left')

    return dfmatch.drop(columns=['firm']), no_match, token_frequency

def sequence_uniqueness(tokens, token_frequency_dict):
    """"""
    
    return sum(1 / token_frequency_dict[t] ** 0.5 for t in tokens)
