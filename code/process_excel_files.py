# %%
# Imports and constants

import glob
import os
import pandas as pd

ROOTDIR = os.path.realpath('..')
DATA_DIR = os.path.join(ROOTDIR, 'data')
SOURCE_DATA_DIR = os.path.join(ROOTDIR, 'raw_data')

# %%

def load_prediction(file):
    df = pd.read_excel(file, sheet_name="Predictions_1")
    alias = df.iloc[1, 1]
    df = df.iloc[3:80, 1:]
    return alias, df

def load_all_predictions():
    all_files = glob.glob(os.path.join(
        SOURCE_DATA_DIR, "*.xlsx")
        )
    d = dict()
    for file in all_files:
        alias, pred = load_prediction(file)
        d[alias] = pred
    return d


# %%
d = load_all_predictions()

# %%
