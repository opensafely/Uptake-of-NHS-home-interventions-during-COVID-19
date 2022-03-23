import pandas as pd
import os

# Create population data frame which includes all weeks and dictionary of cohort size for each individual week
def create_population_df(dir:str = "../output/")-> tuple[pd.DataFrame, dict]:
    # find the input csv files
    filepaths = [f for f in os.listdir(dir) if (f.startswith('input') and f.endswith('.csv'))]
    # append the directory path to filename
    filepaths_dir = [dir + filepath for filepath in filepaths]

    # create empty list to append dataframes
    dfs = []
    # create empty dictionary to store the size of the cohorts (i.e. patients with oximetry codes) each week
    cohort_size = {}

    for file in filepaths_dir:
        # read in files
        output=pd.read_csv(file)
        # Get the index date from the filename
        index_date = pd.to_datetime(file.split("_", )[1].split(".csv")[0], dayfirst=True)
        # Add the index date to the file
        output["index_date"] = index_date
        # Append the dataframes to the list
        dfs.append(output)
        # Note the number of patients in the file for that index date
        cohort_size[index_date] = len(output)
    # Combine all the dataframes together
    population_df = pd.concat(dfs)
    return population_df, cohort_size

