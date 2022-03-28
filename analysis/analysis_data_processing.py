import pandas as pd
import os
from typing import Tuple
import math

# Create population data frame which includes all weeks and dictionary of cohort size for each individual week
def create_population_df(dir:str = "../output/")-> Tuple[pd.DataFrame, dict]:
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


# Helper function for redact_and_round_df
# Takes a column of data, redacts any values less than or equal to 5 and rounds all other values up to nearest 5
def redact_and_round_column(column: pd.Series) -> pd.Series:
    # New column variable will contain the new values with any necessary redacting and rounding applied
    new_column = []
    # For loop to apply redacting and rounding to all integer or float values in the column
    for value in column:
        if type(value) == int or type(value) == float:
            # Redact values less than or equal to 5
            if value <= 5:
                value = "[REDACTED]"
            # Round all values greater than 5 to nearest 5
            else:
                value = int(5 * math.ceil(float(value) / 5))
        # Resulting value is added to the new column
        new_column.append(value)
    return(new_column)


# Funtion to take a dataframe, redact any values less than or equal to 5 and round all other values up to nearest 5
def redact_and_round_df(df: pd.DataFrame) -> pd.DataFrame:
    # Apply redacting and rounding to each column of the dataframe
    for column in df.columns.values:
        df[column] = redact_and_round_column(df[column])
    return(df)
