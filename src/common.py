
import hashlib
import string
import re
from datetime import datetime


def __hash(value, n=8):
    """String hashing to integer"""

    return int(hashlib.sha256(value.encode('utf-8')).hexdigest(), 16) % 10**n


def to_clean_tokens(firmname):
    """String to tokens - filtered out spaces, puncts and to lower cases"""

    full_punctuation = string.punctuation + '’'
    translator = str.maketrans(full_punctuation, ' '*len(full_punctuation))

    firmname = double_to_single_spaces(firmname)
    tokens = firmname.translate(translator).split()
    tokens_cleans = [re.sub("[^0-9a-zA-Z]+", "", t).lower() for t in tokens]
    tokens_filtered = list(set([t for t in tokens_cleans if len(t) > 0]))#.sort(reverse=True)

    return tokens_filtered


def to_clean_string(firmname):
    """String to clean string - filtered out spaces, puncts and to lower cases"""

    full_punctuation = string.punctuation + '’'
    translator = str.maketrans(full_punctuation, ' '*len(full_punctuation))
    firmname = firmname.lower().translate(translator)
    firmname = double_to_single_spaces(firmname).replace(' ', '_')
    return firmname


def double_to_single_spaces(string):
    """Replace double spaces to single space"""

    decrease = 1
    while decrease > 0:
        start_len = len(string)
        string = string.replace('  ', ' ').strip()
        decrease = start_len - len(string)
    return string


def column_to_date(dataf, column):
    """Convert to datetime string"""

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
    """listwise empty and zero values excluded"""

    for c in filterlist:
        n_rows_before = len(dataf)
        dataf = dataf.loc[lambda x: ~x[c].isnull()]
        dataf = dataf.loc[lambda x: x[c]!=0]
        n_rows_filtered = n_rows_before - len(dataf)
        print(f'{c}: {n_rows_filtered} rows are filtered out')

    return dataf


def _filter_on_mins(dataf, filterdict):
    """listwise values excluded based on min value required"""

    for k, v in filterdict.items():
        n_rows_before = len(dataf)
        dataf = dataf.loc[lambda x: ~x[k].isnull()]
        dataf = dataf.loc[lambda x: x[k]>=v]
        n_rows_filtered = n_rows_before - len(dataf)
        print(f'{k}: {n_rows_filtered} rows are filtered out')

    return dataf
