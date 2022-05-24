# Script to create timeseries of pulse oximetry codes usage

from importlib.abc import ResourceReader
import matplotlib.pyplot as plt
import sys
import numpy as np
import pandas as pd
from typing import List

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import (
    create_population_df,
    redact_and_round_df,
    redact_and_round_column,
    code_specific_analysis,
    redact_to_five_and_round,
    further_redaction_all,
    produce_plot,
    add_age_category,
    add_age_and_shielding_column,
    replace_values,
    age_and_shielding_breakdown,
    number_of_uses_of_code,
    code_combinations,
    homecare_title,
    region_list,
)


def analysis_timeseries(homecare_type: str, headers_dict: dict):
    """Function to produce timeseries plot"""

    # Create population data frame which includes all weeks and dictionary of
    # cohort size for each individual week
    population_df, cohort_size = create_population_df(homecare_type)

    # Create data frame of sum totals for each index date for each oximetry code
    sum_df = population_df.groupby(["index_date"], as_index=False)[
        list(headers_dict.values())
    ].sum()
    # Redact values less than or equal to 5 and round all other values up to
    # nearest 5
    sum_df = redact_and_round_df(sum_df)

    # Save the dataframe in outputs folder
    sum_df.to_csv("output/" + homecare_type + "_table_counts.csv")

    # Create timeseries of codes usage
    title = homecare_title(homecare_type)
    sum_df.set_index("index_date", inplace=True)
    produce_plot(sum_df, "Use of " + title + " Over Time", "Date")
    plt.savefig("output/" + homecare_type + "_plot_timeseries", bbox_inches="tight")


def analysis_region(homecare_type: str, headers_dict: dict):
    """Function to produce timeseries plots for each region"""

    # Create population data frame which includes all weeks and dictionary of
    # cohort size for each individual week
    population_df, cohort_size = create_population_df(homecare_type)

    # Create data frame of sum totals for each index date for each oximetry code
    sum_regions = population_df.groupby(["index_date", "region"], as_index=False)[
        list(headers_dict.values())
    ].sum()

    # Apply redaction to entire data frame
    for header in list(headers_dict.values()):
        sum_regions = redact_to_five_and_round(sum_regions, header)
  
    # Save the dataframe
    sum_regions.to_csv("output/" + homecare_type + "_table_counts_allregions.csv")
    
    # Define homecare title for plot
    title = homecare_title(homecare_type)

    # For each region
    for region in region_list:
        # Extract all rows for that region
        region_df = sum_regions.loc[sum_regions["region"] == region]
        # Save the dataframe in outputs folder
        region_df.to_csv("output/" + homecare_type + "_table_counts_" + region + ".csv")
        # Create timeseries of pulse oximetry codes usage
        region_df.set_index("index_date", inplace=True)
        produce_plot(
            region_df,
            "Use of " + title + " Over Time in " + region + " Region",
            "Date",
        )
        plt.savefig(
            "output/" + homecare_type + "_plot_timeseries_region_" + region,
            bbox_inches="tight",
        )


def analysis_breakdowns(homecare_type: str, codes_dict: dict, codes_of_interest):
    """Function to run analysis of timeseries broken down by
    age category, shielding status, sex, IMD decile, ethnicity,
    care home residency and age_plus_shielding_status
    for codes of interest"""

    # Create population data frame which includes all weeks and dictionary of
    # cohort size for each individual week
    population_df, cohort_size = create_population_df(homecare_type)

    # Add age category column to population dataframe
    age_bins = [0, 40, 50, 65, 2000]
    population_df = add_age_category(population_df, age_bins)

    # Add age_and_shielding column
    population_df = add_age_and_shielding_column(population_df)

    # Replace binary flags and abbreviations with meaningful values
    population_df = replace_values(
        population_df,
        "care_home",
        [1, 0],
        ["Care home resident", "Not a care home resident"],
    )
    population_df = replace_values(population_df, "sex", ["M", "F"], ["Male", "Female"])
    population_df = replace_values(
        population_df, "shielding", [1, 0], ["Shielding", "Not shielding"]
    )

    # Define variables of interest and corresponding plot titles
    variable_and_title = {
        "sex": "sex",
        "care_home": "care home residency",
        "shielding": "shielding status",
        "age_group": "age",
        "ethnicity": "ethnicity",
        "imd_quintile": "IMD quintile (1 = most deprived, 5 = least deprived)",
    }

    # Create timeseries for the codes broken down by the variables of interest
    for code in codes_of_interest:
        for variable, title in variable_and_title.items():
            code_specific_analysis(
                homecare_type, code, variable, population_df, codes_dict, title
            )

    # Create timeseries for specific codes broken down by age and shielding status
    age_and_shielding_breakdown(
        homecare_type, codes_dict, population_df, codes_of_interest
    )


def code_analysis(homecare_type: str, headers_dict: dict):
    """Function to summarise how many times patients received each code over the
    entire time period and how many times each possible combination of codes occured"""
    
    # Create population data frame which includes all weeks and dictionary of
    # cohort size for each individual week
    population_df, cohort_size = create_population_df(homecare_type)

    # Create list of relevant headers of population dataframe
    headers = list(headers_dict.values())

    # Total the number of codes per patient over the full time period
    patient_code = population_df.groupby("patient_id")[headers].sum().reset_index()

    # Summarise number of uses of each code for each patient
    number_of_uses_of_code(homecare_type, headers, patient_code)

    # Summarise all code combinations used over time period
    if len(headers) > 1:
        code_combinations(homecare_type, patient_code)
