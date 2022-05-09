# Script to create timeseries of pulse oximetry codes usage

import pandas as pd
import matplotlib.pyplot as plt
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import (
    create_population_df,
    redact_and_round_df,
    produce_plot,
)

# Create population data frame which includes all weeks and dictionary of
# cohort size for each individual week
population_df, cohort_size = create_population_df("output/")

# Create lists of current and required headers
# Convert pulse oximetry codelist csv into data frame
oximetry_codes_df = pd.read_csv("codelists/opensafely-pulse-oximetry.csv")
# Extract list of SNOMED codes
oximetry_codes_list = oximetry_codes_df["code"].tolist()
# List of pulse oximetry headers in population dataframe
oximetry_codes_headers = [f"pulse_oximetry_{x}" for x in oximetry_codes_list]
# List of headers using descriptions as required
oximetry_headers = oximetry_codes_df["term"].tolist()

# Create dictionary for renaming oximetry headers
oximetry_dictionary = {}
for n in range(0, len(oximetry_codes_df)):
    oximetry_dictionary[oximetry_codes_headers[n]] = oximetry_headers[n]

# Create data frame of sum totals for each index date for each oximetry code
oximetry_sum = population_df.groupby(["index_date"], as_index=False)[
    oximetry_codes_headers
].sum()
# Rename oximetry headers in oximetry sums data frame
oximetry_sum.rename(columns=oximetry_dictionary, inplace=True)
# Redact values less than or equal to 5 and round all other values up to
# nearest 5
oximetry_sum = redact_and_round_df(oximetry_sum)

# Save the dataframe in outputs folder
oximetry_sum.to_csv("output/table_1_oximetry_counts.csv")

# Create timeseries of pulse oximetry codes usage
oximetry_sum.set_index("index_date", inplace=True)
produce_plot(oximetry_sum, "Use of Pulse Oximetry Codes Over Time", "Date")
plt.savefig("output/plot_1_oximetry_timeseries", bbox_inches="tight")
