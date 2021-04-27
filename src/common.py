
import hashlib
import string
import re
from datetime import datetime


def __hash(value, n=8):
    """"""

    return int(hashlib.sha256(value.encode('utf-8')).hexdigest(), 16) % 10**n


def to_clean_tokens(firmname):
    """"""

    full_punctuation = string.punctuation + '’'
    translator = str.maketrans(full_punctuation, ' '*len(full_punctuation))

    firmname = double_to_single_spaces(firmname)
    tokens = firmname.translate(translator).split()
    tokens_cleans = [re.sub("[^0-9a-zA-Z]+", "", t).lower() for t in tokens]
    tokens_filtered = list(set([t for t in tokens_cleans if len(t) > 0]))#.sort(reverse=True)

    return tokens_filtered


def to_clean_string(firmname):
    """"""

    full_punctuation = string.punctuation + '’'
    translator = str.maketrans(full_punctuation, ' '*len(full_punctuation))
    firmname = firmname.lower().translate(translator)
    firmname = double_to_single_spaces(firmname).replace(' ', '_')
    return firmname


def double_to_single_spaces(string):
    """"""

    decrease = 1
    while decrease > 0:
        start_len = len(string)
        string = string.replace('  ', ' ').strip()
        decrease = start_len - len(string)
    return string


def column_to_date(dataf, column):
    """"""

    raw_dates = dataf[column].values

    new_dates = []
    for rd in raw_dates:
        succeed = False
        try:
            nd = datetime.strptime(rd, '%d/%m/%Y')
            succeed = True
        except:
            pass
        if not succeed:
            try:
                nd = datetime.strptime(f'01/01/{rd}', '%d/%m/%Y')
                succeed = True
            except:
                pass
        if succeed:
            new_dates.append(nd.strftime('%Y-%m-%d'))
        else:
            new_dates.append(None)

    dataf[column] = new_dates

    return dataf


def _filter_out_nulls(dataf, filterlist):
    """"""

    for c in filterlist:
        n_rows_before = len(dataf)
        dataf = dataf.loc[lambda x: ~x[c].isnull()]
        dataf = dataf.loc[lambda x: x[c]!=0]
        n_rows_filtered = n_rows_before - len(dataf)
        print(f'{c}: {n_rows_filtered} rows are filtered out')

    return dataf


def _filter_on_mins(dataf, filterdict):
    """"""

    for k, v in filterdict.items():
        n_rows_before = len(dataf)
        dataf = dataf.loc[lambda x: ~x[k].isnull()]
        dataf = dataf.loc[lambda x: x[k]>v]
        n_rows_filtered = n_rows_before - len(dataf)
        print(f'{k}: {n_rows_filtered} rows are filtered out')

    return dataf


def create_dummies(dataf, columns):
    """"""

    for c in columns:
        for d in dataf[c].unique():
            dataf[f'dummy_{c}_{d}'] = 0
            dataf.loc[lambda x: x[c].isnull(), f'dummy_{c}_{d}'] = None
            dataf.loc[lambda x: x[c]==d, f'dummy_{c}_{d}'] = 1

    return dataf


def normalize(values):
    """"""

    return [(x-min(values))/(max(values)-min(values)) for x in values]
