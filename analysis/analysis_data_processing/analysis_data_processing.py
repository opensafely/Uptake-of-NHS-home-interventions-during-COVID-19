from typing import Dict
import pandas as pd
import os
import math
import numpy as np
import matplotlib.pyplot as plt
from textwrap import wrap
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.redaction import *
from analysis.codelist import oximetry_codes_dict, bp_codes_dict, proactive_codes_dict


def create_headers_dict(homecare_type: str) -> Dict:
    """Fucntion to create header dictionary for the given homecare type,
    whose keys are the headers in input csv files (i.e. healthcare_at_home_code)
    and values are the terms they refer to"""
    # Find correct codes dictionary
    codes_dict_name = f"{homecare_type}_codes_dict"
    codes_dict = globals()[codes_dict_name]
    # Convert codes to headers used in population dataframe
    headers_dict = {f"healthcare_at_home_{k}": v for k, v in codes_dict.items()}
    return headers_dict


def create_population_df(homecare_type: str, dir: str) -> pd.DataFrame:
    """Function to create population data frame for a particular homecare type
    which includes all weeks and create a dictionary of cohort size for each
    individual week"""
    # find the input csv files
    filepaths = [
        f
        for f in os.listdir(dir)
        if (f.startswith(f"input_{homecare_type}") and f.endswith(".csv"))
    ]
    # append the directory path to filename
    filepaths_dir = [dir + filepath for filepath in filepaths]

    # create empty list to append dataframes
    dfs = []

    for file in filepaths_dir:
        # read in files
        output = pd.read_csv(file)
        # Add the index date to the file by extracting index from filename
        output["index_date"] = pd.to_datetime(
            file.split("_",)[4].split(
                ".csv"
            )[0],
            dayfirst=True,
        )
        # Append the dataframes to the list
        dfs.append(output)

    # Combine all the dataframes together
    population_df = pd.concat(dfs)

    # Rename the headers
    headers_dict = create_headers_dict(homecare_type)
    population_df.rename(columns=headers_dict, inplace=True)

    return population_df


def convert_weekly_to_monthly(
    counts_table: pd.DataFrame, column_name: str
) -> pd.DataFrame:
    """Converts a counts table of practice-level weekly counts to counts aggregated
    every 4 weeks. Where the number of weeks is not divisible by 4, the earliest weeks
    are dropped to ensure number of weeks is a multiple of 4.
    """

    dates = counts_table["index_date"].sort_values(ascending=True).unique()

    # drop earliest weeks if number of weeks not a multiple of 4.
    num_dates = len(dates)
    num_dates_over = num_dates % 4
    if num_dates_over != 0:
        # drop rows from counts table
        counts_table = counts_table.loc[
            ~counts_table["index_date"].isin(dates[0:num_dates_over]),
            counts_table.columns,
        ]

        # drop dates from dates list
        dates = dates[num_dates_over:]

    # create 4 weekly date
    dates_map = {}
    for i in range(0, len(dates), 4):
        date_group = dates[i : i + 4]
        for date in date_group:
            dates_map[date] = date_group[0]
    counts_table.loc[counts_table.index, "index_date"] = counts_table.loc[
        counts_table.index, "index_date"
    ].map(dates_map)

    # group into 4 weeks
    counts_table = (
        (
            counts_table.groupby(by=[column_name, "index_date"])[
                ["counts", "denominators"]
            ]
            .sum()
            .reset_index()
        )
        .sort_values(by=["index_date"])
        .reset_index(drop=True)
    )

    return counts_table


def create_monthly_counts_table(
    codes_df: pd.DataFrame,
    counts_df: pd.DataFrame,
    column_name: str,
) -> pd.DataFrame:
    """Function to take a weekly counts dataframe,
    change it to monthly, apply redacting and rounding
    and add denominators and percentages"""

    # Denominator is total cohort size for that index date
    counts_df["denominators"] = counts_df["index_date"].map(
        (codes_df.groupby("index_date").size()).to_dict()
    )

    # Round the weekly denominators up to nearest 5
    for i, row in counts_df.iterrows():
        counts_df.at[i, "denominators"] = int(
            5 * math.ceil(float(counts_df.loc[i, "denominators"]) / 5)
        )

    # Convert to monthly table
    counts_df = convert_weekly_to_monthly(counts_df, column_name)

    # Exclude denominators which are less than 100 (higher variation will make
    # timeseries less meaningful)
    counts_df["denominators"][counts_df["denominators"] <= 100] = "Less than 100"

    # Apply redacting and rounding to the counts
    counts_df = redact_to_five_and_round(counts_df, "counts")

    # Calculate the percentages
    counts_df["percentage"] = round(
        pd.to_numeric(counts_df["counts"], errors="coerce")
        / pd.to_numeric(counts_df["denominators"], errors="coerce")
        * 100,
        1,
    )

    return counts_df


def homecare_type_dir(homecare_type: str) -> Dict[str, str]:
    """Function to return a dictionary containing the input directory
    (location of the relevant input csv files) and output directory (where to
    store the analysis outputs) for a specific homecare type"""
    return dict(
        input_dir=f"output/{homecare_type}/0.2_join_cohorts/",
        output_dir=f"output/{homecare_type}/0.3_analysis_outputs/",
    )
