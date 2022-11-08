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

def load_predictions(file, check_nans=True):
    """
    Load a single prediction file and return alias and prediction df
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
    if check_nans and nan_values(df_p):  # Check that everything important is filled out
        raise Exception(f"Empty values in {file}. Fix this and run again.")
    return alias, df_p

def load_all_predictions():
    """
    Loop over all prediction files and return a dict {alias: df_prediction}
    """
    all_files = glob.glob(os.path.join(
        SOURCE_DATA_DIR, "*.xlsx")
        )
    d = dict()
    for file in all_files:
        alias, df = load_predictions(file)
        if alias in d:  # Check that there is no name clash
            raise Exception(f"Repeated alias in {file}. Fix this and run again.")
        else:
            # Replace remaining nan values
            df.iloc[:, :4] = df.iloc[:, :4].replace('nan', '')
            df.iloc[:, :4] = df.iloc[:, :4].replace('<NA>', '')
            # Add to dict
            d[alias] = df
    return d

def remove_superfluous_rows(df):
    # Define rows that don't matter
    superfluous_rows = [
        0, 7, 14, 21, 28, 35, 42, 49, 56, 65, 70, 73, 75]
    superfluous_idx = [i + 3 for i in superfluous_rows]
    df2 = df.drop(superfluous_idx)
    return df2

def nan_values(df):
    """
    Test whether there are NaNs in relevant places
    """
    df2 = remove_superfluous_rows(df)
    nan_sum = df2.isnull().sum().sum()
    if nan_sum > 0:
        print(f"There are {nan_sum} NaN values")
        return True
    else:
        return False  

def save_predictions(d):
    """
    Save predictions to individual CSV files
    """
    for alias, pred in d.items():
        filepath = os.path.join(DATA_DIR, f"{alias}.csv")
        print(f"Saving {filepath}")
        pred.to_csv(filepath, index=False, na_rep='', sep=';')
    # Save a file with all aliases
    aliases = list(d.keys())
    aliases.sort(key=str.lower)  # sort alphabetically
    df = pd.DataFrame(aliases, columns=['alias'])
    print(f"Saving aliases.csv")
    df.to_csv(os.path.join(DATA_DIR, "aliases.csv"), index=False, sep=';')
    return None

def save_predictions_excel(d):
    """
    Save predictions to a single Excel file
    """
    filepath = os.path.join(DATA_DIR, "predictions.xlsx")
    aliases = list(d.keys())
    aliases.sort(key=str.lower)  # sort alphabetically
    with pd.ExcelWriter(filepath) as writer:
        print(f"Saving {filepath}")
        for alias in aliases:
            sheet_name = alias
            print(f"Writing sheet {sheet_name}")
            pred = d[alias]
            pred.to_excel(
                writer, sheet_name=sheet_name, index=False, na_rep='')
    return None


# %%
if __name__ == '__main__':
    d = load_all_predictions()
    save_predictions(d)
    save_predictions_excel(d)

