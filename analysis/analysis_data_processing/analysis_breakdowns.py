from os import strerror
import numpy as np
import pandas as pd
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.analysis_data_processing import (
    create_population_df,
    homecare_type_dir,
    create_monthly_counts_table,
)
from analysis.analysis_data_processing.plot import *
from analysis.analysis_data_processing.redaction import *


def add_age_category(population_df: pd.DataFrame) -> pd.DataFrame:
    """Function to add age_group column to dataframe"""

    population_df.loc[population_df["age"] <= 39, "age_group"] = "Age 0-39"
    population_df.loc[population_df["age"].between(40, 49), "age_group"] = "Age 40-49"
    population_df.loc[population_df["age"].between(50, 64), "age_group"] = "Age 50-64"
    population_df.loc[population_df["age"] >= 65, "age_group"] = "Age 65 or over"

    return population_df


def code_time_analysis(
    homecare_type: str,
    code: str,
    variable: str,
    variable_title,
    population_df: pd.DataFrame,
):
    """Function to take a SNOMED code and save the timeseries and
    its underlying table, grouped by a specific column"""

    dirs = homecare_type_dir(homecare_type)

    # Population of interest is all patients with the code
    codes_df = population_df.loc[population_df[f"healthcare_at_home_{code}"] > 0]

    # Count the number of patients in each group for each index date
    summary_df = (
        codes_df.groupby(["index_date", variable])["patient_id"].nunique().reset_index()
    )
    summary_df.rename(columns={"patient_id": "number_of_patients"}, inplace=True)

    # Add denominators and percentages, change dataframe to monthly and redact and round
    summary_df = create_monthly_counts_table(codes_df, summary_df, variable)

    # Save the dataframe in outputs folder
    summary_df.to_csv(
        f"""{dirs["output_dir"]}{homecare_type}_table_code_{code}_{variable}_counts.csv"""
    )

    # Produce the required timeseries
    produce_pivot_plot(
        homecare_type,
        summary_df,
        code,
        variable,
        variable_title,
        "number_of_patients",
    )


def analysis_breakdowns(homecare_type: str, codes_of_interest: list):
    """Function to run analysis of timeseries broken down by
    age category, shielding status, sex, IMD decile, ethnicity,
    care home residency and age_plus_shielding_status
    for codes of interest"""

    dirs = homecare_type_dir(homecare_type)

    # Create population data frame which includes all weeks and dictionary of
    population_df = create_population_df(homecare_type, dirs["input_dir"])

    # Add age category column to population dataframe
    population_df = add_age_category(population_df)

    # Replace binary flags and abbreviations with meaningful values
    population_df["care_home"] = population_df["care_home"].replace(
        to_replace=[1, 0], value=["Care home resident", "Not a care home resident"]
    )
    population_df["sex"] = population_df["sex"].replace(
        to_replace=["M", "F"], value=["Male", "Female"]
    )
    population_df["shielding"] = population_df["shielding"].replace(
        to_replace=[1, 0], value=["Shielding", "Not shielding"]
    )

    # Define variables of interest and corresponding plot titles
    variable_and_title = {
        "sex": "sex",
        "care_home": "care home residency",
        "shielding": "shielding status",
        "age_group": "age",
        "ethnicity": "ethnicity",
        "imd_quintile": "IMD quintile (1 = most deprived, 5 = least deprived)",
        "rural_urban_classification": "rural classification",
        "has_hypertension_code": "hypertension",
        "has_diabetes_type_2_code": "diabetes type 2",
        "has_asthma_code": "asthma",
        "has_copd_code": "copd",
        "has_atrial_fibrillation_code": "artial_fibrillation",
    }

    # Create timeseries for the codes broken down by the variables of interest
    for code in codes_of_interest:
        for variable, title in variable_and_title.items():
            code_time_analysis(homecare_type, code, variable, title, population_df)


def analysis_region(homecare_type: str, codes: list):
    """Function to produce timeseries plots for each region"""

    dirs = homecare_type_dir(homecare_type)

    codes = ["healthcare_at_home_" + s for s in codes]

    # Create population data frame which includes all weeks and dictionary of
    # cohort size for each individual week
    population_df = create_population_df(homecare_type, dirs["input_dir"])

    # Create list of regions in the data
    region_list = population_df["region"].unique()

    # Create data frame of sum totals for each index date for each oximetry code
    sum_regions = population_df.groupby(["index_date", "region"], as_index=False)[
        codes
    ].sum()

    # Apply redaction to entire data frame
    for header in codes:
        sum_regions = redact_to_five_and_round(sum_regions, header)

    # Save the dataframe
    sum_regions.to_csv(
        dirs["output_dir"] + homecare_type + "_table_counts_allregions.csv"
    )

    # Define homecare title for plot
    title = homecare_title(homecare_type)

    # For each region
    for region in region_list:
        # Extract all rows for that region
        region_df = sum_regions.loc[sum_regions["region"] == region]
        # Save the dataframe in outputs folder
        region_df.to_csv("output/" + homecare_type + "_table_counts_" + region + ".csv")
        # Create timeseries of codes usage
        region_df.set_index("index_date", inplace=True)
        try:
            produce_plot(
                region_df,
                "Use of " + title + " Over Time in " + region + " Region",
                "Date",
            )
            plt.savefig(
                dirs["output_dir"]
                + homecare_type
                + "_plot_timeseries_region_"
                + region,
                bbox_inches="tight",
            )
        except:
            pass


def analysis_timeseries(homecare_type: str, codes: list):
    """Function to produce timeseries plot"""

    dirs = homecare_type_dir(homecare_type)

    codes = ["healthcare_at_home_" + s for s in codes]

    # Create population dataframe which includes all weeks and dictionary of
    # cohort size for each individual week
    population_df = create_population_df(homecare_type, dirs["input_dir"])

    # Create dataframe of sum totals for each index date
    sum_df = population_df.groupby(["index_date"], as_index=False)[codes].sum()
    # Redact values less than or equal to 5 and round all other values up to
    # nearest 5
    sum_df = redact_and_round_df(sum_df)

    # Save the dataframe in outputs folders
    sum_df.to_csv(dirs["output_dir"] + homecare_type + "_table_counts.csv")

    # Create timeseries of codes usage
    title = homecare_title(homecare_type)
    sum_df.set_index("index_date", inplace=True)
    produce_plot(sum_df, "Use of " + title + " Over Time", "Date")
    plt.savefig(
        dirs["output_dir"] + homecare_type + "_plot_timeseries", bbox_inches="tight"
    )
