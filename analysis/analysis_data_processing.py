import pandas as pd
import os
from typing import Tuple
import math
import numpy as np
import matplotlib.pyplot as plt
from textwrap import wrap

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


# Helper funtion for code_specific_analysis function. Takes a dataframe countaining a column of counts and
# redacts all counts for an index date if any one of the counts for that date is already redacted
def further_redaction(counts_df: pd.DataFrame) -> pd.DataFrame:
    # For  each row of the dataframe
    for index, row in counts_df.iterrows():
        # If count redacted
        if row['counts'] == '[REDACTED]':
            # Find  its index date
            removal_index = row['index_date']
            # Redact counts for all rows with that index date
            counts_df.loc[counts_df["index_date"] == removal_index, "counts"] = '[REDACTED]'
    return(counts_df)


# Function to take a pulse oximetry code and save the timeseries and its underlying table, grouped by a specific column
def code_specific_analysis(code: str, column_name: str, population_df: pd.DataFrame, oximetry_codes_dict: dict):
    # Population of interest is all patients with the code
    codes_df = population_df.loc[population_df['pulse_oximetry_' + code] == 1]
    # Count the number of patients in each age group for each index date
    counts_df = codes_df.groupby(['index_date', column_name]).size().reset_index()
    counts_df.rename(columns={0: 'counts'},inplace=True)

    # Count the denominator (the total size of the cohort for each week)
    counts_df['denominators'] = counts_df['index_date'].map((codes_df.groupby('index_date').size()).to_dict()) 
    # Apply redacting and rounding to the counts
    counts_df['counts'] = redact_and_round_column(counts_df['counts'])
    # Redact counts for any week where at least one count has been redacted
    counts_df = further_redaction(counts_df)
    # Exclude denominators which are less than 100 (higher variation will make timeseries less meaningful)
    counts_df['denominators'] = np.where(counts_df['denominators'] >= 100, counts_df['denominators'], 'Less than 100')
    # Calculate the percentages (where possible i.e. when count not redacted and denominator >=100)
    counts_df['percentage'] = round(pd.to_numeric(counts_df['counts'], errors='coerce') / pd.to_numeric(counts_df['denominators'], errors = 'coerce') * 100, 1)

    # Save the dataframe in outputs folder
    counts_df.to_csv('output/tables/table_' + code + '_' + column_name + '_counts.csv') 

    # Plot the counts over time (pivot to create separate columns for each grouping)
    plot_timeseries = counts_df.pivot(index="index_date", columns= column_name, values="percentage").plot(figsize=(20,10), fontsize = 20).get_figure()
    plt.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize = 20)
    plt.xlabel("Date", fontsize = 25)
    plt.ylabel('Percentage of patients', fontsize = 25)
    plt.title('\n'.join(wrap('Patients with \"' + oximetry_codes_dict[int(code)] + '\" code,\n grouped by ' + column_name)), fontsize = 40)