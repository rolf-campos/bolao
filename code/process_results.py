# %%
from datetime import datetime
import os
import pandas as pd
from process_excel_files import load_predictions, remove_superfluous_rows


ROOTDIR = os.path.realpath('..')
DATA_DIR = os.path.join(ROOTDIR, 'data')
ASSET_DIR = os.path.join(ROOTDIR, 'assets')
OUTPUT_DIR = os.path.join(ROOTDIR, 'table')

# %%
# Helper functions to load from result/predition files
def load_results():
    """
    Load results XLSX file and return two databases,
    one for the first round, and one for the second.
    """
    results_file = os.path.join(ASSET_DIR, 'results.xlsx')
    _, df = load_predictions(results_file, check_nans=False)
    df = remove_superfluous_rows(df)
    df_1 = df.loc[:59, :]  # first round
    df_2 = df.loc[59:, :]  # second round
    assert len(df_1) == 48
    assert len(df_2) == 16
    return df_1, df_2

def load_prediction_csv(alias):
    """
    Load CSV file of an alias and return two databases,
    one for the first round, and one for the second.
    """
    file = os.path.join(DATA_DIR, f"{alias}.csv")
    df = pd.read_csv(file, sep=';')
    superfluous_rows = [
        0, 7, 14, 21, 28, 35, 42, 49, 56, 65, 70, 73, 75]
    df_p = df.drop(superfluous_rows)
    # Convert floats to ints
    columns_int = ['id 1', 'id 2', 'Goals 1', 'Goals 2']
    df_p.loc[:, columns_int] = df_p[columns_int].astype('Int64')
    df_1 = df_p.loc[:56, :]  # first round
    df_2 = df_p.loc[56:, :]  # second round
    assert len(df_1) == 48
    assert len(df_2) == 16
    return df_1, df_2

def load_all_predictions(aliases):
    """
    Load all predictions from CSV files
    Returns a dict with structure {alias: (df_1, df_2)}
    """
    d = dict()
    for alias in aliases:
        d[alias] = load_prediction_csv(alias)
    return d

# Helper functions to award points
def wtl(g1, g2):
    """
    Evaluate whether team 1 [W]on / [T]ied / [L]ost
    """
    if g1 > g2:  # team 1 won
        return 'W'
    elif g1 < g2:  # team 1 lost
        return 'L'
    else:  # tie
        return 'T'

def points_from_match(result, guess):
    """
    Compute points from a first-stage match
    results and guess must be a tuple or list of two ints
    """
    points = 0
    if wtl(*result) == wtl(*guess):  # correct winner
        points += 6
        # conditional on correct winner, award points for goals
        if result[0] == guess[0]:
            points += 2
        if result[1] == guess[1]:
            points += 2
    return points

def points_from_stage_1(df_r, df_g):
    """
    Compute all points in stage 1 for guess df_g based on results in df_r 
    """
    results = df_r[['Goals 1', 'Goals 2']].values
    guesses = df_g[['Goals 1', 'Goals 2']].values
    points = 0
    for r, g in zip(results, guesses):
        if not pd.isna(r[1]):  # if there is a result
            points += points_from_match(r, g)
    return points

def points_from_stage_2(df_r, df_g):
    """
    Compute all points in stage 2 for guess df_g based on results in df_r 
    """
    # Define rows
    rows_R16 = range(0, 8)
    rows_QF = range(8, 12) 
    rows_df = range(12, 14)
    row_3rd = 14
    row_final = 15

    # Round of 16
    R16_1 = df_r.iloc[rows_R16, 0].tolist()
    R16_2 = df_r.iloc[rows_R16, 0].tolist()
    # Get rid of NaNs
    R16_1 = clean(R16_1)
    R16_2 = clean(R16_2)
    return 0

def clean(rlist, words=['nan', '<NA>']):
    res = list(rlist)  # make a copy
    for word in words:
        res = [r for r in res if r != word]
    return res


def evaluate(stage_2=False):
    df_r1, df_r2 = load_results()
    df_a = pd.read_csv(os.path.join(DATA_DIR, 'aliases.csv'))
    aliases = list(df_a['alias'])
    d = load_all_predictions(aliases)
    table = []
    for alias in aliases:
        df_g1, df_g2 = d[alias]
        points_1 = points_from_stage_1(df_r1, df_g1)
        if stage_2:  # stage 2 has started
            points_2 = points_from_stage_1(df_r2, df_g2)
        else:
            points_2 = 0
        row = [alias, points_1, points_2, points_1 + points_2]
        table.append(row)
    df = pd.DataFrame(
        table,
        columns=['Alias', 'Stage 1', 'Stage 2', 'Total']
        )
    df.sort_values(by='Total', ascending=False, inplace=True)
    df.insert(0, 'Position', list(range(1, len(df)+1)))
    return df

# %%
if __name__ == '__main__':
    df = evaluate()
    # Save with today's date
    date_today = datetime.today().strftime('%Y-%m-%d')
    standings_file = os.path.join(OUTPUT_DIR, f'standings_{date_today}.csv')
    print(f"Saving {standings_file}")
    df.to_csv(standings_file, index=False, sep=';')
    # and overwrite the version without a date
    standings_file_no_date = os.path.join(OUTPUT_DIR, 'standings.csv')
    print(f"Saving (and probably overwriting) {standings_file_no_date}")
    df.to_csv(standings_file_no_date, index=False, sep=';')


# %%
