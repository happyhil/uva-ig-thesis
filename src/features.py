import numpy as np
import string
import statistics
from scipy import stats
from src import common, string_matching


def generate_csr_index(dataf, elements):
    """Generates CSR index based on stenghts and concerns from MSCI KLD social stats database."""

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
    """Generate number of existance in data breaches (PRC) database."""

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


def create_composite_variable(dataf, feature_dict, method):
    """
    Combines formative constructs into one composite variable.
    For continues variables, scale method can be 'minmax' or 'zscore'.
    """

    combination = []
    for k, v in feature_dict['features'].items():

        if v['type'] == 'continues':
            newcol = f'{k}_standardized'
            raw_values = dataf[k].astype(float).values
            if method == 'minmax':
                dataf[newcol] = min_max_standardization(raw_values)
            elif method == 'zscore':
                dataf[newcol] = zscore_standardization(raw_values)
            else:
                print(f'unknown standardization method given for {k}')
                break
        elif v['type'] == 'binary':
            newcol = k
            dataf[newcol] = dataf[newcol].astype(int)
        else:
            print(f'unknown dtype in dict for {k}')
            break

        if v['best_value'] == 0:
            prevcol = newcol
            newcol = f'{newcol}_reverse'
            dataf[newcol] = 1 - dataf[prevcol]

        combination.append(newcol)

    dataf[feature_dict['name']] = dataf[combination].sum(axis=1) / len(combination)

    return dataf


def data_checks(dataf, column, print_results=True):
    """Checks and prints data stats: mean, std, kurt, skew, and p value for normal test."""

    result =  {
        'mean': round(dataf[column].mean(), 2),
        'std': round(dataf[column].std(), 2),
        'kurtosis': round(stats.kurtosis(dataf[column]), 2),
        'skew': round(stats.skew(dataf[column]), 2),
        'p_normal_test': round(stats.normaltest(dataf[column])[1], 3),
    }

    if print:
        if result['p_normal_test'] <= 0.001:
            sig = '***'
        elif result['p_normal_test'] <= 0.01:
            sig = '**'
        elif result['p_normal_test'] <= 0.05:
            sig = '*'
        else:
            sig = ''
        print(f"""{column}: mean = {result['mean']}; std = {result['std']}; kurtosis = {result['kurtosis']}; skew = {result['skew']}; p value normal test = {result['p_normal_test']}{sig}""")

    return result

def create_dummies(dataf, columns):
    """Creates dummies for given columns."""

    for c in columns:
        for d in dataf[c].unique():
            dataf[f'dummy_{c}_{d}'] = 0
            dataf.loc[lambda x: x[c].isnull(), f'dummy_{c}_{d}'] = None
            dataf.loc[lambda x: x[c]==d, f'dummy_{c}_{d}'] = 1

    return dataf


def min_max_standardization(values):
    """Returns scores between min and max of original values."""

    return [(x-min(values))/(max(values)-min(values)) for x in values]


def zscore_standardization(values):
    """Returns z scores of original values."""

    mean = sum(values) / len(values)
    stdev = statistics.stdev(values)
    return [(x - mean) / stdev for x in values]


def log_transform(values, lowest_value_before_transform=None):
    """Log transformation on given values."""

    if lowest_value_before_transform != None:
        if min(values) < lowest_value_before_transform:
            diff = lowest_value_before_transform - min(values)
            return [np.log(v+diff) for v in values]
        else:
            return [np.log(v) for v in values]

    return [np.log(v) for v in values]


def sqrt_transform(values):
    """Square root transformation on given values."""

    return [np.sqrt(v) for v in values]
