import pandas as pd
import os
from typing import Tuple
import math
import numpy as np
import matplotlib.pyplot as plt
from textwrap import wrap


# ============================================================================================
# Functions
# ============================================================================================


def create_population_df(
    homecare_type: str, dir: str = "output/completed/"
) -> Tuple[pd.DataFrame, dict]:
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
    # create empty dictionary to store the size of the cohorts
    # (i.e. patients with oximetry codes) each week
    cohort_size = {}

    for file in filepaths_dir:
        # read in files
        output = pd.read_csv(file)
        # Get the index date from the filename
        index_date = pd.to_datetime(
            file.split("_",)[2].split(
                ".csv"
            )[0],
            dayfirst=True,
        )
        # Add the index date to the file
        output["index_date"] = index_date
        # Append the dataframes to the list
        dfs.append(output)
        # Note the number of patients in the file for that index date
        cohort_size[index_date] = len(output)
    # Combine all the dataframes together
    population_df = pd.concat(dfs)
    if homecare_type == "oximetry":
        population_df.rename(columns=oximetry_headers_dict, inplace=True)
    elif homecare_type == "bp":
        population_df.rename(columns=bp_headers_dict, inplace=True)
    elif homecare_type == "proactive":
        population_df.rename(columns=proactive_headers_dict, inplace=True)
    return population_df, cohort_size


def redact_and_round_column(column: pd.Series) -> pd.Series:
    """Function which takes a column of data, redacts any values less than or
    equal to 5 and rounds all other values up to nearest 5"""
    # New column variable will contain the new values with any necessary
    # redacting and rounding applied
    new_column = []
    # For loop to apply redacting and rounding to all integer or float values
    # in the column
    for value in column:
        if type(value) == int or type(value) == float:
            # Redact values less than or equal to 5
            if value <= 5:
                value = "[REDACTED]"
            # Round all values greater than 5 up to nearest 5
            else:
                value = int(5 * math.ceil(float(value) / 5))
        # Resulting value is added to the new column
        new_column.append(value)
    return new_column


def redact_to_five_and_round(
    counts_df: pd.DataFrame, column_to_redact: str
) -> pd.DataFrame:
    """Function which determines for each index date if any value in a dataframe column
    is <= 5 and if so redacts all values <=5 then continues redacting the next lowest
    value until the redacted values add up to >= 5.
    All remaining values are then rounded up to nearest 5"""
    # For each index date
    for index_date in counts_df.index_date.unique():
        # Create temporary dataframe of all the rows with that index date
        temp_df = counts_df[counts_df["index_date"] == index_date]
        # If sum of values in the column <= 5
        if pd.to_numeric(temp_df[column_to_redact], errors="coerce").sum() <= 5:
            # Redact all values in the column
            temp_df[column_to_redact] = "[REDACTED]"
        # Else if there are any numbers <= 5 in the column of interest
        elif (
            pd.to_numeric(
                temp_df[column_to_redact][
                    pd.to_numeric(temp_df[column_to_redact], errors="coerce") <= 5
                ],
                errors="coerce",
            ).count()
            > 0
        ):
            # Store total quantity redacted
            total_redacted = 0
            # For each row
            for index in temp_df.index.values:
                # If column value is less than 5
                if (
                    pd.to_numeric(temp_df.loc[index, column_to_redact], errors="coerce")
                    <= 5
                ):
                    # Add to the total_redacted variable
                    total_redacted += temp_df.loc[index, column_to_redact]
                    # Redact the value
                    temp_df.loc[index, column_to_redact] = "[REDACTED]"
                    # While total_redacted <= 5
                    while total_redacted <= 5:
                        # Find index of the lowest non-redacted count for that index date
                        min_index = pd.to_numeric(
                            temp_df[temp_df[column_to_redact] != "[REDACTED]"][
                                column_to_redact
                            ]
                        ).idxmin()
                        # Add to the total_redacted variable
                        total_redacted += temp_df.loc[min_index, column_to_redact]
                        # Redact the value
                        temp_df.at[min_index, column_to_redact] = "[REDACTED]"
        # Update counts dataframe with the redactions
        counts_df.update(temp_df)
    # Round all numeric values in column up to nearest 5
    for index in counts_df.index.values:
        value = counts_df.loc[index, column_to_redact]
        if type(value) != str:
            counts_df.loc[index, column_to_redact] = int(
                5 * math.ceil(float(value) / 5)
            )
    return counts_df


def redact_and_round_df(df: pd.DataFrame) -> pd.DataFrame:
    """Function to take a dataframe, redact any values less than or equal to 5 and
    round all other values up to nearest 5"""
    # Apply redacting and rounding to each column of the dataframe
    for column in df.columns.values:
        df[column] = redact_and_round_column(df[column])
    return df


def further_redaction_all(counts_df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Function which takes a dataframe countaining a column of counts and
    redacts all counts for an index date if any one of the counts for that
    date is already redacted"""
    # For  each row of the dataframe
    for index, row in counts_df.iterrows():
        # If count redacted
        if row[column_name] == "[REDACTED]":
            # Find  its index date
            removal_index = row["index_date"]
            # Redact counts for all rows with that index date
            counts_df.loc[
                counts_df["index_date"] == removal_index, column_name
            ] = "[REDACTED]"
    return counts_df


def further_redaction(counts_df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Function which takes a dataframe and redacts smallest remaining value
    in a column for each index date, if one value in that column is already
    redacted for that index date"""
    # For each index date
    for index_date in counts_df.index_date.unique():
        # Create temporary dataframe of all the rows with that index date
        temp_df = counts_df[counts_df["index_date"] == index_date]
        # Count how many are redacted
        number_of_redactions = temp_df[column_name].to_list().count("[REDACTED]")
        # If one count is redacted
        if number_of_redactions == 1:
            # Find index of the lowest non-redacted count for that index date
            min_index = pd.to_numeric(
                temp_df[temp_df[column_name] != "[REDACTED]"][column_name]
            ).idxmin()
            # Redact it
            temp_df.at[min_index, column_name] = "[REDACTED]"
            # Update counts dataframe with extra redaction
            counts_df.update(temp_df)
    return counts_df


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


def produce_plot(
    df: pd.DataFrame,
    title: str = None,
    x_label: str = None,
    y_label: str = None,
    figure_size: tuple = (20, 10),
):
    """Function to produce plot of all dataframe columns"""
    fig, ax = plt.subplots(figsize=figure_size)
    df.replace(["[REDACTED]"], np.nan).plot(ax=ax)
    plt.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=20)
    plt.xlabel(x_label, fontsize=20)
    plt.ylabel(y_label, fontsize=20)
    plt.title("\n".join(wrap(title)), fontsize=40)


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


def replace_values(
    population_df: pd.DataFrame, column: str, to_replace: list, replace_with: list
) -> pd.DataFrame:
    """Function to replace all values in a column with new values"""
    population_df[column] = population_df[column].replace(
        to_replace=to_replace, value=replace_with
    )

    return population_df


def age_and_shielding_cumulative_labels(counts_df: pd.DataFrame) -> pd.DataFrame:
    """Function to label the cumulative totals for age & shielding status"""

    # Define the groups
    conditionlist = [
        (counts_df["age_and_shielding"] == "1: Shielding"),
        (counts_df["age_and_shielding"] == "2: Aged 65 or over and not shielding"),
        (counts_df["age_and_shielding"] == "3: Aged 50 to 64 and not shielding"),
        (counts_df["age_and_shielding"] == "4: Aged 49 or under and not shielding"),
    ]

    # Define the labels for the cumulative
    choicelist = [
        "Shielding",
        "Shielding or aged 65 or over",
        "Shielding or aged 50 or over",
        "All patients",
    ]

    # Add the labels to the dataframe as a new column
    counts_df["cumulative_age_and_shielding"] = np.select(
        conditionlist, choicelist, default="Not Specified"
    )

    return counts_df


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
    if column_name == "age_and_shielding":
        counts_df["counts"] = redact_and_round_column(counts_df["counts"])
        counts_df = further_redaction_all(counts_df, "counts")
    else:
        counts_df = redact_to_five_and_round(counts_df, "counts")

    # Calculate the percentages
    counts_df["percentage"] = round(
        pd.to_numeric(counts_df["counts"], errors="coerce")
        / pd.to_numeric(counts_df["denominators"], errors="coerce")
        * 100,
        1,
    )

    return counts_df


def produce_pivot_plot(
    homecare_type: str,
    counts_df: pd.DataFrame,
    code: str,
    term: str,
    column_name: str,
    variable_title: str,
    pivot_values: str,
    reorder_legend: list = None,
):
    """Function to create timeseries of code of interest broken down
    by variable of interest"""

    # Pivot based on column of interest
    pivot_df = counts_df.pivot(
        index="index_date",
        columns=column_name,
        values=pivot_values,
    )

    # Produce plot
    plot_title = 'Patients with "' + term + '" code, grouped by ' + variable_title
    produce_plot(pivot_df, plot_title, x_label="Date", y_label="Percentage")

    # Reorder legend if required
    if reorder_legend is not None:
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(
            [handles[i] for i in reorder_legend],
            [labels[i] for i in reorder_legend],
            loc="upper left",
            bbox_to_anchor=(1.0, 1.0),
            fontsize=20,
        )

    # Save plot
    plt.savefig(
        "output/"
        + homecare_type
        + "_plot_code_"
        + code
        + "_"
        + column_name
        + "_timeseries.png",
        bbox_inches="tight",
    )


def age_and_shielding_breakdown(
    homecare_type: str,
    codes_dict: dict,
    population_df: pd.DataFrame,
    codes_of_interest: dict,
):
    """Function to create breakdown by age combined with shielding status"""
    for code in codes_of_interest:

        # Find the term associated with the code
        term = codes_dict[int(code)]

        # Population of interest is all patients with the code
        codes_df = population_df.loc[population_df[term] == 1]

        # Count the number of patients in each age_and_shielding group for each
        # index date
        counts_df = (
            codes_df.groupby(["index_date", "age_and_shielding"]).size().reset_index()
        )
        counts_df.rename(columns={0: "counts"}, inplace=True)

        # Add denominators and percentages, change dataframe to monthly and redact and round
        counts_df = create_monthly_counts_table(
            codes_df, counts_df, column_name="age_and_shielding"
        )

        # Create column containing labels for cumulative percentages
        counts_df = age_and_shielding_cumulative_labels(counts_df)

        # Create column of cumulative percentages based on age and shielding status
        # for each index date
        counts_df["cumulative_age_and_shielding_percentages"] = np.nan
        for index_date in counts_df.index_date.unique():
            counts_df["cumulative_age_and_shielding_percentages"][
                counts_df["index_date"] == index_date
            ] = counts_df["percentage"][counts_df["index_date"] == index_date].cumsum()

        # Save the dataframe in outputs folder
        counts_df.to_csv(
            "output/"
            + homecare_type
            + "_table_code_"
            + code
            + "_cumulative_age_and_shielding_counts.csv"
        )

        # Produce the required timeseries
        produce_pivot_plot(
            homecare_type,
            counts_df,
            code,
            term,
            "cumulative_age_and_shielding",
            "age and shielding status",
            "cumulative_age_and_shielding_percentages",
            [0, 2, 3, 1],
        )


def code_specific_analysis(
    homecare_type: str,
    code: str,
    column_name: str,
    population_df: pd.DataFrame,
    codes_dict: dict,
    variable_title: str = None,
):
    """Function to take a pulse oximetry code and save the timeseries and
    its underlying table, grouped by a specific column"""

    # Find the term associated with the code
    term = codes_dict[int(code)]

    # Population of interest is all patients with the code
    codes_df = population_df.loc[population_df[term] == 1]

    # Count the number of patients in each age group for each index date
    counts_df = codes_df.groupby(["index_date", column_name]).size().reset_index()
    counts_df.rename(columns={0: "counts"}, inplace=True)

    # Add denominators and percentages, change dataframe to monthly and redact and round
    counts_df = create_monthly_counts_table(codes_df, counts_df, column_name)

    # Save the dataframe in outputs folder
    counts_df.to_csv(
        "output/"
        + homecare_type
        + "_table_code_"
        + code
        + "_"
        + column_name
        + "_counts.csv"
    )

    # Produce the required timeseries
    produce_pivot_plot(
        homecare_type, counts_df, code, term, column_name, variable_title, "percentage"
    )


def number_of_uses_of_code(
    homecare_type: str, headers: list, patient_code: pd.DataFrame
):
    """Function to summarise how many times patients received each code over the
    entire time period and save the results for each code"""
    i = 1
    for code in patient_code.columns[1:]:
        code_summary = patient_code.groupby(code)["patient_id"].nunique()
        code_summary_df = pd.DataFrame(code_summary)
        code_summary_df.rename(
            columns={"patient_id": "Total number of patients"},
            inplace=True,
        )
        # Round and redact dataframe and save to csv
        redact_and_round_df(code_summary_df).to_csv(
            f"output/{homecare_type}_table_code_counts_{i}_{code}.csv"
        )
        i = i + 1


def code_combinations(
    homecare_type: str,
    patient_code: pd.DataFrame,
):
    """Function to determine how many times each possible combination
    of codes occured"""
    # Set the index of the dataframe to be patient id
    patient_code.set_index("patient_id", inplace=True, drop=True)

    # Set totals to flags in the patient code dataframe
    patient_code = patient_code.mask(patient_code >= 1, 1)

    # Group by all codes and total the number of unique patients
    patient_code = (
        patient_code.reset_index()
        .groupby(patient_code.columns.tolist())["patient_id"]
        .nunique()
    )

    # Convert to dataframe
    patient_code = pd.DataFrame(patient_code)

    # Rename column header
    patient_code.rename(
        columns={"patient_id": "Total number of uses of the combination"}, inplace=True
    )

    # Round and redact dataframe and save to csv
    redact_and_round_df(patient_code).to_csv(
        f"output/{homecare_type}_table_code_combinations.csv"
    )


def no_codes_used(homecare_type: str):
    """Function to identify index dates for patients with no codes relating to the releveant healthcare type"""
    population_df, cohort_size = create_population_df(
        homecare_type, dir="output/completed/"
    )

    # Consider the number of unique patients
    population_df = population_df.drop_duplicates(subset=["patient_id"])

    # Condition is that all columns relating to SNOMED codes for that homecare_type are 0
    if homecare_type == "oximetry":
        condition_list = (
            (population_df["Telehealth pulse oximetry monitoring started"] == 0)
            & (population_df["Telehealth pulse oximetry monitoring ended"] == 0)
            & (population_df["Provision of pulse oximeter"] == 0)
            & (
                population_df["Telehealth pulse oximetry monitoring not appropriate"]
                == 0
            )
            & (population_df["Telehealth pulse oximetry monitoring declined"] == 0)
            & (
                population_df[
                    "Referral to telehealth pulse oximetry monitoring service"
                ]
                == 0
            )
            & (
                population_df[
                    "Referral by telehealth pulse oximetry monitoring service"
                ]
                == 0
            )
            & (
                population_df[
                    "Discharge from telehealth pulse oximetry monitoring service"
                ]
                == 0
            )
            & (
                population_df["Discussion about telehealth pulse oximetry monitoring"]
                == 0
            )
            & (population_df["Has access to pulse oximeter"] == 0)
            & (population_df["Oxygen saturation at periphery unknown"] == 0)
            & (population_df["Oxygen saturation at periphery equivocal"] == 0)
        )
    elif homecare_type == "bp":
        condition_list = (
            (population_df["Average day interval systolic blood pressure"] == 0)
            & (population_df["Average day interval diastolic blood pressure"] == 0)
            & (population_df["Average home diastolic blood pressure"] == 0)
            & (population_df["Average home systolic blood pressure"] == 0)
        )
    elif homecare_type == "proactive":
        condition_list = population_df["Provision of proactive care"] == 0

    # Extract those with none of the relevant SNOMED codes
    no_codes_used = population_df.loc[condition_list]
    # Identify the index dates for those patients
    no_codes_used = no_codes_used["index_date"].value_counts().to_frame()

    # Round and redact dataframe and save to csv
    redact_and_round_df(no_codes_used).to_csv(
        f"output/{homecare_type}_table_no_codes_used.csv"
    )


def homecare_title(homecare_type):
    """Function to return title for plots based on homecare type"""
    if homecare_type == "oximetry":
        title = "Pulse Oximetry Codes"
    elif homecare_type == "bp":
        title = "Blood Pressure Monitoring Codes"
    elif homecare_type == "proactive":
        title = "Procative Care Code"
    return title


# ============================================================================================
# Variables
# ============================================================================================

# Codes dictionaries: Keys are SNOMED codes, values are the terms they refer to
oximetry_codes_df = pd.read_csv("codelists/opensafely-pulse-oximetry.csv")
oximetry_codes_dict = oximetry_codes_df.set_index("code")["term"].to_dict()
bp_codes_dict = {
    413606001: "Average home systolic blood pressure",
    314446007: "Average day interval systolic blood pressure",
    413605002: "Average home diastolic blood pressure",
    314461008: "Average day interval diastolic blood pressure",
}
proactive_codes_dict = {934231000000106: "Provision of proactive care"}


# Headers dictionaries:
# Keys are oximetry headers in input csv files (i.e. healthcare_at_home_code),
# values are the terms they refer to
oximetry_headers_dict = {
    f"healthcare_at_home_{k}": v for k, v in oximetry_codes_dict.items()
}
bp_headers_dict = {f"healthcare_at_home_{k}": v for k, v in bp_codes_dict.items()}
proactive_headers_dict = {
    f"healthcare_at_home_{k}": v for k, v in proactive_codes_dict.items()
}
