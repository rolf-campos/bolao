# %%
# Imports and constants

import glob
import os
import pandas as pd

ROOTDIR = os.path.realpath('..')
DATA_DIR = os.path.join(ROOTDIR, 'data')
SOURCE_DATA_DIR = os.path.join(ROOTDIR, 'raw_data')

# %%
# Functions to extract predictions from the Excel files

def load_prediction(file):
    """
    Load a single prediction and return alias and prediction df
    """
    df = pd.read_excel(file, sheet_name="Predictions_1")
    alias = df.iloc[1, 1]
    df_p = df.iloc[3:80, 1:]
    # Nice column names
    cols = [
        "id 1",
        "Team 1",
        "id 2",
        "Team 2",
        "Goals 1",
        "Goals 2"
    ]
    df_p.columns = cols
    # Convert to correct types
    dtypes = [str]*4 + ['Int64']*2
    type_conversion = {k: v for (k, v) in zip(cols, dtypes)}
    df_p["id 2"] = df_p["id 2"].astype('Int64').astype(str)
    df_p = df_p.astype(type_conversion)
    return alias, df_p

def load_all_predictions():
    """
    Loop over all predictions and return a dict {alias: df_prediction}
    """
    all_files = glob.glob(os.path.join(
        SOURCE_DATA_DIR, "*.xlsx")
        )
    d = dict()
    for file in all_files:
        alias, df = load_prediction(file)
        if alias in d:
            # Check that there is no name clash
            raise Exception(f"Repeated alias in {file}. Fix this and run again.")
        elif nan_values(df):
            # Check that everything important is filled out
            raise Exception(f"Empty values in {file}. Fix this and run again.")
        else:
            # Replace remaining nan values
            df.iloc[:, :4] = df.iloc[:, :4].replace('nan', '')
            df.iloc[:, :4] = df.iloc[:, :4].replace('<NA>', '')
            d[alias] = df
    return d

def nan_values(df):
    # Define rows that don't matter
    superfluous_rows = [0, 7, 14, 21, 28, 35, 42, 49, 56, 65, 70, 73, 75]
    superfluous_idx = [i + 3 for i in superfluous_rows]
    df2 = df.drop(superfluous_idx)
    nan_sum = df2.isnull().sum().sum()
    if nan_sum > 0:
        print(f"There are {nan_sum} NaN values")
        return True
    else:
        return False  

def save_predictions(d):
    for alias, pred in d.items():
        filepath = os.path.join(DATA_DIR, f"{alias}.csv")
        print(f"Saving {filepath}")
        pred.to_csv(filepath, index=False, na_rep='', sep=';')
    return None

# %%
d = load_all_predictions()
save_predictions(d)

# %%
