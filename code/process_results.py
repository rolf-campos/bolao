# %%
import os
import pandas as pd
from process_excel_files import load_predictions, remove_superfluous_rows


ROOTDIR = os.path.realpath('..')
DATA_DIR = os.path.join(ROOTDIR, 'data')
ASSET_DIR = os.path.join(ROOTDIR, 'assets')

# %%
def load_results():
    results_file = os.path.join(ASSET_DIR, 'results.xlsx')
    _, df = load_predictions(results_file, check_nans=False)
    df = remove_superfluous_rows(df)
    df_1 = df.loc[:59, :]
    df_2 = df.loc[59:, :]
    assert len(df_1) == 48
    assert len(df_2) == 16
    return df_1, df_2

def load_prediction_csv(alias):
    file = os.path.join(DATA_DIR, f"{alias}.csv")
    df = pd.read_csv(file, sep=';')
    superfluous_rows = [
        0, 7, 14, 21, 28, 35, 42, 49, 56, 65, 70, 73, 75]
    df_p = df.drop(superfluous_rows)
    df_1 = df_p.loc[:56, :]
    df_2 = df_p.loc[56:, :]
    assert len(df_1) == 48
    assert len(df_2) == 16
    return df_1, df_2

def load_all_predictions(aliases):
    d = dict()
    for alias in aliases:
        d[alias] = load_prediction_csv(alias)
    return d

def points_stage_1(df, df_results):
    N = len(df)
    assert N == len(df_results)
    g_1 = df['Goals 1'].astype('Int64').values
    g_2 = df['Goals 2'].astype('Int64').values

    rg_1 = df_results['Goals 1'].astype('Int64').values
    rg_2 = df_results['Goals 2'].astype('Int64').values
    
    winner_1 = (g_1 > g_2)
    winner_2 = (g_2 > g_1)
    tie = (g_1 == g_2)
    
    rwinner_1 = (rg_1 > rg_2)
    rwinner_2 = (rg_2 > rg_1)
    rtie = (rg_1 == rg_2)
    return winner_1, winner_2, tie


# %%
df_1, df_2 = load_results()
df_a = pd.read_csv(os.path.join(DATA_DIR, 'aliases.csv'))
aliases = list(df_a['alias'])
d = load_all_predictions(aliases)

# %%
