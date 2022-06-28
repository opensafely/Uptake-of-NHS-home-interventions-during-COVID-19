from typing import Dict
import pandas as pd
import os
import math
import numpy as np
import matplotlib.pyplot as plt
from textwrap import wrap
from redaction import *


# ============================================================================================
# Functions
# ============================================================================================


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

    filepaths_dir

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


# def create_monthly_counts_table(
#     codes_df: pd.DataFrame,
#     counts_df: pd.DataFrame,
#     column_name: str,
# ) -> pd.DataFrame:
#     """Function to take a weekly counts dataframe,
#     change it to monthly, apply redacting and rounding
#     and add denominators and percentages"""

#     # Denominator is total cohort size for that index date
#     counts_df["denominators"] = counts_df["index_date"].map(
#         (codes_df.groupby("index_date").size()).to_dict()
#     )

#     # Round the weekly denominators up to nearest 5
#     for i, row in counts_df.iterrows():
#         counts_df.at[i, "denominators"] = int(
#             5 * math.ceil(float(counts_df.loc[i, "denominators"]) / 5)
#         )

#     # Convert to monthly table
#     counts_df = convert_weekly_to_monthly(counts_df, column_name)

#     # Exclude denominators which are less than 100 (higher variation will make
#     # timeseries less meaningful)
#     counts_df["denominators"][counts_df["denominators"] <= 100] = "Less than 100"

#     # Apply redacting and rounding to the counts
#     if column_name == "age_and_shielding":
#         counts_df["counts"] = redact_and_round_column(counts_df["counts"])
#         counts_df = further_redaction_all(counts_df, "counts")
#     else:
#         counts_df = redact_to_five_and_round(counts_df, "counts")

#     # Calculate the percentages
#     counts_df["percentage"] = round(
#         pd.to_numeric(counts_df["counts"], errors="coerce")
#         / pd.to_numeric(counts_df["denominators"], errors="coerce")
#         * 100,
#         1,
#     )

#     return counts_df


def homecare_type_dir(homecare_type: str) -> Dict[str, str]:
    return dict(
        input_dir=f"../../output/{homecare_type}/0.2_join_cohorts/",
        output_dir=f"../../output/{homecare_type}/0.3_analysis_outputs/",
    )
