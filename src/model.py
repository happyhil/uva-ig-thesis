
import pandas as pd
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler


def OLSModel(dataf, x_columns, y_column, scale=False):
    """"""

    if scale:
        scaler = StandardScaler()
        df_X_train = pd.DataFrame(scaler.fit_transform(dataf[x_columns]), columns=x_columns)
    else:
        df_X_train = pd.DataFrame(dataf[x_columns], columns=x_columns)

    df_X_train['constant'] = 1

    df_y_train = dataf[[y_column]]
    model = sm.OLS(df_y_train, df_X_train).fit()

    return model
