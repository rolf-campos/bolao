# %% Imports and constants
import os
import pandas as pd
import random
from openpyxl import load_workbook

ROOTDIR = os.path.realpath('..')
ASSET_DIR = os.path.join(ROOTDIR, 'assets')
RAW_DATA_DIR = os.path.join(ROOTDIR, 'raw_data')

# Cells that need to be filled
COLS_GROUP = [
    'B', 'C', 'E', 'F', 'H', 'I', 'K', 'L', 'N', 'O',
    'Q', 'R', 'T', 'U', 'W', 'X']
ROWS_GROUP = [str(14 + 5*i) for i in range(6)]
CELLS_GROUP = [c + r for r in ROWS_GROUP for c in COLS_GROUP]
CELLS_R16 = [c + '51' for c in COLS_GROUP]
CELLS_QF = [c + '61' for c in ['C', 'E', 'I', 'K', 'O', 'Q', 'U', 'W']]
CELLS_SF = ['F71', 'H71', 'R71', 'T71']
CELLS_F = ['L79', 'N79', 'L89', 'N89']
CELLS = CELLS_GROUP + CELLS_R16 + CELLS_QF + CELLS_SF + CELLS_F
assert len(CELLS) == 128

# %% Functions
def macaco(seed):
    """
    Generate pseudorandom numbers for the Macaco based on a seed value
    """
    random.seed(seed)

    # Generate goal counts for the group stage
    num_groups = 8
    matches_per_group = 6
    teams_per_match = 2
    N_goals = num_groups * matches_per_group * teams_per_match
    goals = [random.randint(0, 2) for _ in range(N_goals)]

    # Generate winners for the knockout stage
    # 0: the first team is the winner; 1: the second team is the winner
    N_winners = 8 + 4 + 2 + 2
    winners = [random.randint(0, 1) for _ in range(N_winners)]

    # Convert winners to goals and concatenate
    all_goals = goals + convert_winners_to_goals(winners)
    return all_goals

def convert_winners_to_goals(winners):
    """
    Convert winners and losers into goal counts
    """
    goals = []
    for w in winners:
        if w == 0:  # generate a 1-0 result
            goals.append(1)
            goals.append(0)
        else:  # generate a 0-1 result
            goals.append(0)
            goals.append(1)
    return goals

def run_main():
    # Set seed to the date of the final and generate goals
    seed = 20221218
    goals = macaco(seed)
    assert len(goals) == len(CELLS)

    # Load the Excel file
    loadpath = os.path.join(ASSET_DIR, 'Qatar_2022.xlsx')
    wb = load_workbook(loadpath, keep_vba=True)

    # Fill in alias/name in the instructions sheet
    sheet_instructions = wb.worksheets[0]
    sheet_instructions['C3'] = 'Macaco'  # alias
    sheet_instructions['C4'] = 'Macaco'  # name
    sheet_instructions['C5'] = 'N/A'  # email

    # Fill in the goals sheet
    sheet = wb.worksheets[1]
    for cell, g in zip(CELLS, goals):
        sheet[cell] = g

    # Save the completed Excel file
    savepath = os.path.join(RAW_DATA_DIR, 'Macaco.xlsx')
    wb.save(savepath)

# %%
if __name__ == '__main__':
    run_main()
