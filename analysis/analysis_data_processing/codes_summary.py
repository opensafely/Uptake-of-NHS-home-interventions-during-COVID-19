import pandas as pd
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.analysis_data_processing import (
    create_headers_dict,
    create_population_df,
    homecare_type_dir,
)
from analysis.analysis_data_processing.redaction import redact_and_round_df


def number_of_uses_of_code(homecare_type: str, df: pd.DataFrame):
    """Function to summarise how many times patients received each code over the
    entire time period and save the results for each code"""

    dirs = homecare_type_dir(homecare_type)

    i = 1
    for header in df.columns[1:]:
        code_summary = df.groupby(header)["patient_id"].nunique()
        code_summary_df = pd.DataFrame(code_summary)
        code_summary_df.rename(
            columns={"patient_id": "Total number of patients"},
            inplace=True,
        )
        # Round and redact dataframe and save to csv
        redact_and_round_df(code_summary_df).to_csv(
            f"""{dirs["output_dir"]}{homecare_type}_table_code_counts_{i}_{header.replace (" ", "_")}.csv"""
        )
        i = i + 1


def code_combinations(
    homecare_type: str,
    df: pd.DataFrame,
):
    """Function to determine how many times each possible combination
    of codes occured"""

    dirs = homecare_type_dir(homecare_type)

    # Set the index of the dataframe to be patient id
    df.set_index("patient_id", inplace=True, drop=True)

    # Set totals to flags in the patient code dataframe
    df = df.mask(df >= 1, 1)

    # Group by all codes and total the number of unique patients
    df = df.reset_index().groupby(df.columns.tolist())["patient_id"].nunique()

    # Convert to dataframe
    df = pd.DataFrame(df)

    # Rename column header
    df.rename(
        columns={"patient_id": "Total number of uses of the combination"}, inplace=True
    )

    # Round and redact dataframe and save to csv
    redact_and_round_df(df).to_csv(
        dirs["output_dir"] + homecare_type + "_table_code_combinations.csv"
    )


def code_population(homecare_type: str, df: pd.DataFrame, headers: str):
    """Function to sumamrise how many patients received each SNOMED code
    each week"""

    dirs = homecare_type_dir(homecare_type)

    i = 1
    for header in headers:
        code_summary = df[df[header] > 0]
        code_summary = code_summary.groupby(["index_date"])["patient_id"].nunique()
        code_summary_df = pd.DataFrame(code_summary)
        code_summary_df.rename(
            columns={"patient_id": "Total number of patients"},
            inplace=True,
        )
        # Round and redact dataframe and save to csv
        redact_and_round_df(code_summary_df).to_csv(
            f"""{dirs["output_dir"]}{homecare_type}_table_patient_id_total_{i}_{header.replace (" ", "_")}.csv"""
        )
        i = i + 1


def code_analysis(homecare_type: str):
    """Function to summarise how many times patients received each code over the
    entire time period and how many times each possible combination of codes occured"""

    dirs = homecare_type_dir(homecare_type)

    # Create list of relevant headers of population dataframe
    headers_dict = create_headers_dict(homecare_type)
    headers = list(headers_dict.values())

    # Create population data frame which includes all weeks and dictionary of
    # cohort size for each individual week
    population_df = create_population_df(homecare_type, dirs["input_dir"])

    # Total the number of codes per patient over the full time period
    patient_codes = population_df.groupby("patient_id")[headers].sum().reset_index()

    # Summarise number of uses of each code for each patient
    number_of_uses_of_code(homecare_type, patient_codes)

    # Summarise all code combinations used over time period
    code_combinations(homecare_type, patient_codes)

    # Summarise how many patients received each code each week
    code_population(homecare_type, population_df, headers)
