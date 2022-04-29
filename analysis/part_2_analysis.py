import sys
import pandas as pd

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import (
    create_population_df,
    redact_and_round_df,
)

# Create population data frame which includes all weeks and dictionary of
# cohort size for each individual week
population_df, cohort_size = create_population_df("output/")


# ============================================================================================
# Number of patient codes assigned to a patient over the time period
# ============================================================================================

# Total the number of codes per patient over the full time period
patient_code = (
    population_df.groupby("patient_id")[
        "pulse_oximetry_1325191000000108",
        "pulse_oximetry_1325201000000105",
        "pulse_oximetry_1325211000000107",
        "pulse_oximetry_1325221000000101",
        "pulse_oximetry_1325241000000108",
        "pulse_oximetry_1325251000000106",
        "pulse_oximetry_1325261000000109",
        "pulse_oximetry_1325271000000102",
        "pulse_oximetry_1325281000000100",
        "pulse_oximetry_1325681000000102",
        "pulse_oximetry_1325691000000100",
        "pulse_oximetry_1325701000000100",
    ]
    .sum()
    .reset_index()
)

# Summarise how many patients recieved each code over the time period
i = 1
for code in patient_code.columns[1:]:
    code_summary = patient_code.groupby(code)["patient_id"].nunique()
    code_summary_df = pd.DataFrame(code_summary)
    # Round and redact dataframe and save to csv
    redact_and_round_df(code_summary_df).to_csv(
        f"output/table_{i}_oximetry_code_counts_{code}.csv"
    )
    i = i + 1

# ============================================================================================
# Number of codes assigned to a patient over the time period
# ============================================================================================

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

# Create dictionary of oximetry codes: keys are SNOMED codes, values are the
# terms they refer to
oximetry_codes_df = pd.read_csv("codelists/opensafely-pulse-oximetry.csv")
oximetry_codes_dict = oximetry_codes_df.set_index("code")["term"].to_dict()
# Create dictionary of oximetry headers:
# Keys are oximetry headers in input csv files (i.e. pulse_oximetry_code),
# values are the terms they refer to
oximetry_headers_dict = {
    f"pulse_oximetry_{k}": v for k, v in oximetry_codes_dict.items()
}
# Rename column headers to code names
patient_code.rename(columns=oximetry_headers_dict, inplace=True)

# Round and redact dataframe and save to csv
redact_and_round_df(patient_code).to_csv(
    f"output/table_{i}_oximetry_code_combinations.csv"
)
