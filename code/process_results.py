# %%
from datetime import datetime
import os
import pandas as pd
from process_excel_files import load_predictions, remove_superfluous_rows


ROOTDIR = os.path.realpath('..')
DATA_DIR = os.path.join(ROOTDIR, 'data')
ASSET_DIR = os.path.join(ROOTDIR, 'data')
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
    points = 0
    # Round of 16 (16 points missing here)
    points += points_round_of_16(df_r, df_g)
    # Quarter final
    rows_QF = range(8, 12)
    points += points_round(df_r, df_g, rows_QF)
    # Semi final
    rows_SF = range(12, 14)
    points += points_round(df_r, df_g, rows_SF)
    # Getting to the final
    row_final = range(15, 16)
    points += points_round(df_r, df_g, row_final)
    # Identity of champion and 3rd place
    points += points_winner(df_r, df_g)
    points += points_winner(df_r, df_g, third_place=True)
    return points

def points_winner(df_r, df_g, third_place=False):
    """
    Award points for correctly guessing the winner
    of the final and the third place game
    """
    # Parameters
    if third_place:
        row = 14
        point_value = 10
    else:
        row = 15
        point_value = 30
    # Load results and guesses
    r = df_r.iloc[row, :]  # result
    g = df_g.iloc[row, :]  # guess
    # Determine winner
    if (pd.isna(r[4]) or pd.isna(r[5])):
        winner = 'Not available yet'
    elif r[4] > r[5]:
        winner = r[1]
    else:
        winner = r[3]
    if g[4] > g[5]:
        winner_g = g[1]
    else:
        winner_g = g[3]
    # Assign points
    points = 0
    if winner == winner_g:
        points += point_value
    return points

def points_round(df_r, df_g, rows, point_value=10):
    """
    Award points from reaching a certain round
    The variable "rows" indicates the rows in the df to be evaluated
    """
    # Results for the round
    R_1 = df_r.iloc[rows, 1].tolist()
    R_2 = df_r.iloc[rows, 3].tolist()
    # Get rid of NaNs
    R_1_clean = clean(R_1)
    R_2_clean = clean(R_2)
    # Predictions for the round
    G_1 = df_g.iloc[rows, 1].tolist()
    G_2 = df_g.iloc[rows, 3].tolist()
    # Award points
    points = 0
    for id in R_1_clean + R_2_clean:
        if id in G_1:
            points += point_value
        if id in G_2:
            points += point_value
    return points

def points_round_of_16(df_r, df_g):
    """
    Award points for reaching the round of 16.
    Also awards extra points for getting the order right.
    """
    # Points from advancing into the round of 16
    rows_R16 = range(0, 8)
    points = points_round(df_r, df_g, rows_R16, point_value=3)

    # Additional points (1st and 2nd in group)
    # Need to infer first and second in group from matches
    # Locations of first and second in match table:
    A = [(0, 0), (4,1)]
    C = [(1, 0), (5,1)]
    E = [(2, 0), (6,1)]
    G = [(3, 0), (7,1)]
    B = [(4, 0), (0,1)]
    D = [(5, 0), (1,1)]
    F = [(6, 0), (2,1)]
    H = [(7, 0), (3,1)]
    groups = [A, B, C, D, E, F, G, H]
    df_R = df_r[['Team 1', 'Team 2']]  # results
    df_G = df_g[['Team 1', 'Team 2']]  # guess
    for group in groups:
        result_order = (df_R.iloc[group[0]], df_R.iloc[group[1]])
        guess_order =  (df_G.iloc[group[0]], df_G.iloc[group[1]])
        if result_order == guess_order:  # both 1st and 2nd correct
            points += 2
    return points

def clean(rlist, words=['nan', '<NA>']):
    """
    Remove words from a list
    """
    res = list(rlist)  # make a copy of the list
    for word in words:
        res = [r for r in res if r != word]
    return res

# Main function
def evaluate(stage_2=False):
    """
    Build a table with the current standings.
    Optionally, evaluate also stage 2.
    """
    df_r1, df_r2 = load_results()
    df_a = pd.read_csv(os.path.join(DATA_DIR, 'aliases.csv'))
    aliases = list(df_a['alias'])
    d = load_all_predictions(aliases)
    table = []
    for alias in aliases:
        df_g1, df_g2 = d[alias]
        points_1 = points_from_stage_1(df_r1, df_g1)
        if stage_2:
            points_2 = points_from_stage_2(df_r2, df_g2)
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

def test(verbose=False):
    """
    Test that all players get full points if results coincide
    with their predictions.
    """
    df_a = pd.read_csv(os.path.join(DATA_DIR, 'aliases.csv'))
    aliases = list(df_a['alias'])
    d = load_all_predictions(aliases)
    for alias in aliases:
        if verbose:
            print(f"Testing {alias}")
        df_r1, df_r2 = load_prediction_csv(alias)  # use guess as result
        df_g1, df_g2 = d[alias]
        points_1 = points_from_stage_1(df_r1, df_g1)
        points_2 = points_from_stage_2(df_r2, df_g2)
        assert points_1 == 480  # full points stage 1
        assert points_2 == 244  # full points stage 2
    print("Passed all tests.")


# %%
if __name__ == '__main__':
    DISPLAY = True
    # Run test to verify that nothing is broken
    test()
    # Evaluate
    df = evaluate(stage_2=False)
    # Save with today's date
    date_today = datetime.today().strftime('%Y-%m-%d')
    standings_file = os.path.join(OUTPUT_DIR, f'standings_{date_today}.csv')
    print(f"Saving {standings_file}")
    df.to_csv(standings_file, index=False, sep=';')
    # and overwrite the version without a date
    standings_file_no_date = os.path.join(OUTPUT_DIR, 'standings.csv')
    print(f"Saving (and probably overwriting) {standings_file_no_date}")
    df.to_csv(standings_file_no_date, index=False, sep=';')
    if DISPLAY:
        display(df)  # works only in Ipython


# %%
