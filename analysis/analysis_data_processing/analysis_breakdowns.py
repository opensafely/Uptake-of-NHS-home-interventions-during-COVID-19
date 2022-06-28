from os import strerror
import numpy as np
import pandas as pd
from analysis_data_processing import create_population_df, homecare_type_dir
from plot import *
from redaction import *


def add_age_category(population_df: pd.DataFrame, age_bins: list) -> pd.DataFrame:
    """Function to add age category column to dataframe.
    age_bins specifies the required groupings"""

    n = len(age_bins)

    # Create list of labels for the different age groups
    age_group_labels = []
    # Create labels for all except final category
    for i in range(0, len(age_bins) - 2):
        age_group_labels.append(f"Age {age_bins[i]} - {age_bins[i+1]-1}")
    # For final age category the label is 'Age ... or over'
    age_group_labels.append(f"Age {age_bins[-2]} or over")

    # Take 1 from age bins e.g. [0,40] becomes [-1,39], which will find
    # ages such that -1<age<=39 i.e. 0<age<=39 as required
    new_age_bins = [n - 1 for n in age_bins]

    # Create age category column and insert into the population data frame
    age_category = pd.cut(population_df.age, bins=new_age_bins, labels=age_group_labels)
    population_df.insert(0, "age_group", age_category)

    return population_df


def add_age_and_shielding_column(population_df: pd.DataFrame) -> pd.DataFrame:
    """Function to add column for combined age and shielding
    status to dataframe"""

    # Define the conditions for the groupings
    conditionlist = [
        (population_df["shielding"] == 1),
        (population_df["shielding"] == 0) & (population_df["age"] >= 65),
        (population_df["shielding"] == 0)
        & (population_df["age"] >= 50)
        & (population_df["age"] < 65),
        (population_df["shielding"] == 0) & (population_df["age"] < 50),
    ]

    # Define the labels for the groupings
    choicelist = [
        "1: Shielding",
        "2: Aged 65 or over and not shielding",
        "3: Aged 50 to 64 and not shielding",
        "4: Aged 49 or under and not shielding",
    ]

    # Add age_and_shielding column
    population_df["age_and_shielding"] = np.select(
        conditionlist, choicelist, default="Not Specified"
    )

    return population_df


def age_and_shielding_cumulative_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Function to label the cumulative totals for age & shielding status"""

    # Define the groups
    conditionlist = [
        (df["age_and_shielding"] == "1: Shielding"),
        (df["age_and_shielding"] == "2: Aged 65 or over and not shielding"),
        (df["age_and_shielding"] == "3: Aged 50 to 64 and not shielding"),
        (df["age_and_shielding"] == "4: Aged 49 or under and not shielding"),
    ]

    # Define the labels for the cumulative
    choicelist = [
        "Shielding",
        "Shielding or aged 65 or over",
        "Shielding or aged 50 or over",
        "All patients",
    ]

    # Add the labels to the dataframe as a new column
    df["cumulative_age_and_shielding"] = np.select(
        conditionlist, choicelist, default="Not Specified"
    )

    return df


def code_time_analysis(
    homecare_type: str,
    code: str,
    variable: str,
    variable_title,
    population_df: pd.DataFrame,
):
    """Function to take a pulse oximetry code and save the timeseries and
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
    # counts_df = create_monthly_counts_table(codes_df, counts_df, column_name)

    # Save the dataframe in outputs folder
    summary_df.to_csv(
        f"""{dirs["output_dir"]}{homecare_type}_table_code_code_{variable}_counts.csv"""
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
    population_df = add_age_category(population_df, [0, 40, 50, 65, 2000])

    # Add age_and_shielding column
    population_df = add_age_and_shielding_column(population_df)

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
        "age_and_shielding": "age and shielding flag",
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


# def analysis_region(homecare_type: str, headers_dict: dict):
#     """Function to produce timeseries plots for each region"""

#     # Create population data frame which includes all weeks and dictionary of
#     # cohort size for each individual week
#     population_df = create_population_df(homecare_type)

#     # Create list of regions in the data
#     region_list = population_df["region"].unique()

#     # Create data frame of sum totals for each index date for each oximetry code
#     sum_regions = population_df.groupby(["index_date", "region"], as_index=False)[
#         list(headers_dict.values())
#     ].sum()

#     # Apply redaction to entire data frame
#     for header in list(headers_dict.values()):
#         sum_regions = redact_to_five_and_round(sum_regions, header)

#     # Save the dataframe
#     sum_regions.to_csv("output/" + homecare_type + "_table_counts_allregions.csv")

#     # Define homecare title for plot
#     title = homecare_title(homecare_type)

#     # For each region
#     for region in region_list:
#         # Extract all rows for that region
#         region_df = sum_regions.loc[sum_regions["region"] == region]
#         # Save the dataframe in outputs folder
#         region_df.to_csv("output/" + homecare_type + "_table_counts_" + region + ".csv")
#         # Create timeseries of pulse oximetry codes usage
#         region_df.set_index("index_date", inplace=True)
#         try:
#             produce_plot(
#                 region_df,
#                 "Use of " + title + " Over Time in " + region + " Region",
#                 "Date",
#             )
#             plt.savefig(
#                 "output/" + homecare_type + "_plot_timeseries_region_" + region,
#                 bbox_inches="tight",
#             )
#         except:
#             pass


def analysis_timeseries(homecare_type: str, dir: str):
    """Function to produce timeseries plot"""

    dirs = homecare_type_dir(homecare_type)

    # Create population dataframe which includes all weeks and dictionary of
    # cohort size for each individual week
    population_df = create_population_df(homecare_type, dirs["input_dir"])

    # Create dataframe of sum totals for each index date
    sum_df = population_df.groupby("index_date")["patient_id"].nunique()
    # Redact values less than or equal to 5 and round all other values up to
    # nearest 5
    sum_df = redact_and_round_df(sum_df)

    # Save the dataframe in outputs folder
    sum_df.to_csv(dirs["output_dir"] + homecare_type + "_table_counts.csv")

    # Create timeseries of codes usage
    title = homecare_title(homecare_type)
    sum_df.set_index("index_date", inplace=True)
    produce_plot(sum_df, "Use of " + title + " Over Time", "Date")
    plt.savefig(
        dirs["output_dir"] + homecare_type + "_plot_timeseries", bbox_inches="tight"
    )
