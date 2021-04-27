
import string
from src import common, string_matching


def generate_csr_index(dataf, elements):
    """"""

    dataf.columns = [c.lower() for c in dataf.columns]

    firm_csr_scores = {}
    for c in dataf['firmhash'].unique():

        last_available_year = int(dataf.loc[lambda x: x['firmhash']==c]['year'].max())

        element_scores = {}
        for ek, ev in elements.items():

            strenght_columns = [f'{ek}_str_{a}' for a in string.ascii_lowercase if f'{ek}_str_{a}' in dataf.columns]
            concern_columns = [f'{ek}_con_{a}' for a in string.ascii_lowercase if f'{ek}_con_{a}' in dataf.columns]

            dfstrenght = dataf.loc[lambda x: x['firmhash']==c][strenght_columns].fillna(0).replace('R', 0).astype(int)
            dfconcern = dataf.loc[lambda x: x['firmhash']==c][concern_columns].fillna(0).replace('R', 0).astype(int)

            sum_strenghts = dfstrenght.sum().sum()
            max_strenghts = dfstrenght.count().sum()

            sum_concerns = dfconcern.sum().sum()
            max_concerns = dfconcern.count().sum()

            element_scores[ev] = (sum_strenghts - sum_concerns) / (max_strenghts + max_concerns)

        firm_csr_scores[int(c)] = {
            'last_available_year': last_available_year,
            'csr_index': sum([v for v in element_scores.values()]) / 5,
            'csr_index_elements': element_scores
        }

    return firm_csr_scores


def count_prc_existence(df_fortune, df_prc):
    """"""

    fortune_companies = list(df_fortune['firm'].values)
    prc_companies = list(df_prc['Company'].values)

    fortune_companies_tokenized = [common.to_clean_tokens(f) for f in fortune_companies]
    prc_companies_tokenized = [common.to_clean_tokens(f) for f in prc_companies]
    all_companies_tokenized = [*prc_companies_tokenized, *fortune_companies_tokenized]

    token_frequency = string_matching.build_token_frequency_table(all_companies_tokenized)

    prc_existance = {}
    for firmname, firmtokens in zip(fortune_companies, fortune_companies_tokenized):
        prc_existance[common.__hash(firmname)] = 0
        for matchtokens in prc_companies_tokenized:
            matchscore = string_matching.name_similarity(firmtokens, matchtokens, token_frequency)
            if matchscore >= 0.7:
                prc_existance[common.__hash(firmname)] += 1

    return prc_existance, token_frequency


def combine_features(dataf, feature_dict):
    """"""

    combination = []
    for k, v in feature_dict['features'].items():

        if v['type'] == 'continues':
            newcol = f'{k}_normalized'
            raw_values = dataf[k].astype(float).values
            dataf[newcol] = common.normalize(raw_values)
        elif v['type'] == 'binary':
            newcol = k
            dataf[newcol] = dataf[newcol].astype(int)

        if v['best_value'] == 0:
            prevcol = newcol
            newcol = f'{newcol}_reverse'
            dataf[newcol] = 1 - dataf[prevcol]

        combination.append(newcol)

    dataf[feature_dict['name']] = dataf[combination].sum(axis=1) / len(combination)

    return dataf
