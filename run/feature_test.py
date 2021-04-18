#!/usr/bin/env python


import json
from datetime import datetime
import pandas as pd
import itertools
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

Y_COLUMN = 'reputation_score_2020'
# Y_COLUMN = 'reputation_score_growth'
X_COLUMNS = [
    'revenue_in_millions',
    'profits_in_millions',
#     'return_on_assets',
#     'n_employees',
#     'age_in_years',
#     'pp_n_sentence',
#     'pp_number_of_words',
#     'pp_number_of_unique_words',
#     'pp_existence_of_a_transparency_report',
#     'pp_contact_option',
#     'dummy_pp_legislation_complied_with_standard',
#     'dummy_pp_legislation_complied_with_ccpa',
#     'dummy_pp_legislation_complied_with_gdpr',
#     'pp_third_party_sharing',
#     'pp_existence_of_a_data_protection_officer',
#     'pp_iso_type',
#     'pp_ambiquity_score',
#     'pp_gunning_fog_index',
#     'n_data_breaches',
]


def _model(dataf, x_columns, y_column):
    """"""
    
    scaler = StandardScaler() 
    df_X_train = pd.DataFrame(scaler.fit_transform(dataf[x_columns]), columns=x_columns)
    df_X_train['constant'] = 1

    df_y_train = dataf[[y_column]] 
    model = sm.OLS(df_y_train, df_X_train).fit() 

    return model

def list_combination(x_columns):
    """"""

    subcombinations = []
    for i in range(1, len(x_columns)+1):
        comb = [list(x) for x in list(itertools.combinations(x_columns, i))]
        subcombinations.append(comb)
    combinations = [i for l in subcombinations for i in l]
    
    return combinations
    

def run_feature_selection(dataf, x_columns, y_column):
    """"""
    
    combinations = list_combination(x_columns)

    results = {}
    highest_r_adj = 0
    best_features = None
    for n in range(0, len(combinations)):
        model = _model(dataf, combinations[n], y_column)
        if model.rsquared_adj > highest_r_adj:
            highest_r_adj = model.rsquared_adj
            best_features = combinations[n]
        results[n] = {
            'rsquared_adj': model.rsquared_adj,
            'n_significant': len([p for p in model.pvalues.values if p <= 0.05]),
            'features': combinations[n]
        }
        
    return highest_r_adj, best_features, results


def main():
    
    df = pd.read_csv('data/modelinput/information_governance_clean_dataset.csv')
    
    highest_r_adj, best_features, results = run_feature_selection(df, X_COLUMNS, Y_COLUMN)
    
    with open(f'data/modeloutput/feature_fits_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as outfile:
        json.dump(results, outfile)

        
if __name__ == '__main__':
    main()