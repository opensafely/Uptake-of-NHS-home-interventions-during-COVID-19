# Script to create timeseries of pulse oximetry codes usage

import matplotlib.pyplot as plt
import sys
import numpy as np
import pandas as pd

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
    #for header in list(headers_dict.values()):
        #sum_regions = redact_to_five_and_round(sum_regions, header)

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

    # Define the ranges for each of the age categories
    # (e.g. [-1, 39] will find ages such that -1<age<=39 - age is a whole number
    # in the data frame so this is anyone aged 0 to 40 inclusive)
    age_bins = [-1, 0, 39, 49, 64, 110, 2000]
    n = len(age_bins)

    # Create list of labels for the different age groups
    age_group_labels = []
    # For all except the last final age category the label is
    # 'Age between ... and ...'
    for i in range(0, len(age_bins) - 2):
        age_group_labels.append(f"Age {age_bins[i]+1} - {age_bins[i+1]}")
    # For final age category the label is 'Age ... or over'
    age_group_labels.append(f"Age {age_bins[-2]+1} or over")

    # Create list of age category for each patient and insert into the population
    # data frame
    age_category = pd.cut(population_df.age, bins=age_bins, labels=age_group_labels)
    population_df.insert(0, "age_group", age_category)

    # # Add column to population data frame for combined age group and shielding
    # # status
    # conditionlist = [
    #     (population_df["shielding"] == 1),
    #     (population_df["shielding"] == 0) & (population_df["age"] >= 65),
    #     (population_df["shielding"] == 0)
    #     & (population_df["age"] >= 50)
    #     & (population_df["age"] < 65),
    #     (population_df["shielding"] == 0) & (population_df["age"] < 50),
    # ]
    # choicelist = [
    #     "1: Shielding",
    #     "2: Aged 65 or over and not shielding",
    #     "3: Aged 50 to 64 and not shielding",
    #     "4: Aged 49 or under and not shielding",
    # ]
    # population_df["age_and_shielding"] = np.select(
    #     conditionlist, choicelist, default="Not Specified"
    # )

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
        #"care_home": "care home residency",
        #"shielding": "shielding status",
        "age_group": "age",
        #"ethnicity": "ethnicity",
        "imd_quintile": "IMD quintile (1 = most deprived, 5 = least deprived)",
    }

    # Create timeseries for the codes broken down by the variables of interest
    for code in codes_of_interest:
        for key, value in variable_and_title.items():
            code_specific_analysis(
                homecare_type, code, key, population_df, codes_dict, value
            )

    # Create timeseries for specific codes broken down by age and shielding status

    # for code in codes_of_interest:
    #     # Find the term associated with the code
    #     term = codes_dict[int(code)]
    #     # Population of interest is all patients with the code
    #     codes_df = population_df.loc[population_df[term] == 1]
    #     # Count the number of patients in each age_and_shielding group for each
    #     # index date
    #     counts_df = (
    #         codes_df.groupby(["index_date", "age_and_shielding"]).size().reset_index()
    #     )
    #     counts_df.rename(columns={0: "counts"}, inplace=True)
    #     # Count the denominator (the total size of the cohort for each week)
    #     counts_df["denominators"] = counts_df["index_date"].map(
    #         (codes_df.groupby("index_date").size()).to_dict()
    #     )
    #     # Apply redacting and rounding to the counts
    #     #counts_df["counts"] = redact_and_round_column(counts_df["counts"])
    #     # Redact counts for any week where at least one count has been redacted
    #     #counts_df = further_redaction_all(counts_df, "counts")
    #     # Exclude denominators which are less than 100 (higher variation will make
    #     # timeseries less meaningful)
    #     counts_df["denominators"] = np.where(
    #         counts_df["denominators"] >= 100, counts_df["denominators"], "Less than 100"
    #     )
    #     # Calculate the percentages (where possible i.e. when count not redacted
    #     # and denominator >=100)
    #     counts_df["percentage"] = round(
    #         pd.to_numeric(counts_df["counts"], errors="coerce")
    #         / pd.to_numeric(counts_df["denominators"], errors="coerce")
    #         * 100,
    #         1,
    #     )
    #     # Create column containing labels for cumulative percentages
    #     conditionlist = [
    #         (counts_df["age_and_shielding"] == "1: Shielding"),
    #         (counts_df["age_and_shielding"] == "2: Aged 65 or over and not shielding"),
    #         (counts_df["age_and_shielding"] == "3: Aged 50 to 64 and not shielding"),
    #         (counts_df["age_and_shielding"] == "4: Aged 49 or under and not shielding"),
    #     ]
    #     choicelist = [
    #         "Shielding",
    #         "Shielding or aged 65 or over",
    #         "Shielding or aged 50 or over",
    #         "All patients",
    #     ]
    #     counts_df["cumulative_labels"] = np.select(
    #         conditionlist, choicelist, default="Not Specified"
    #     )

    #     # Create column of cumulative percentages based on age and shielding status
    #     # for each index date
    #     counts_df["cumulative_age_and_shielding"] = np.nan
    #     for index_date in counts_df.index_date.unique():
    #         counts_df["cumulative_age_and_shielding"][
    #             counts_df["index_date"] == index_date
    #         ] = counts_df["percentage"][counts_df["index_date"] == index_date].cumsum()
    #     # Save the dataframe in outputs folder
    #     counts_df.to_csv(
    #         "output/"
    #         + homecare_type
    #         + "_table_code_"
    #         + code
    #         + "_age_and_shielding_counts.csv"
    #     )
    #     # Create timeseries plot
    #     pivot_df = counts_df.pivot(
    #         index="index_date",
    #         columns="cumulative_labels",
    #         values="cumulative_age_and_shielding",
    #     )
    #     plot_title = (
    #         'Patients with "'
    #         + term
    #         + '" code, grouped by '
    #         + "age and shielding status"
    #     )
    #     produce_plot(pivot_df, plot_title, x_label="Date")
    #     # Reorder legend labels to match cumulative order
    #     handles, labels = plt.gca().get_legend_handles_labels()
    #     order = [0, 2, 3, 1]
    #     # Add legend
    #     plt.legend(
    #         [handles[i] for i in order],
    #         [labels[i] for i in order],
    #         loc="upper left",
    #         bbox_to_anchor=(1.0, 1.0),
    #         fontsize=20,
    #     )
    #     plt.savefig(
    #         "output/"
    #         + homecare_type
    #         + "_plot_code_"
    #         + code
    #         + "_"
    #         + "age_and_shielding"
    #         + "_timeseries.png",
    #         bbox_inches="tight",
    #     )
