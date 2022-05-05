import pandas as pd
import matplotlib.pyplot as plt
import sys
if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import (
    create_population_df,
    redact_and_round_df,
    further_redaction,
    oximetry_headers_dict,
    redact_to_five_and_round
)


# Create population data frame which includes all weeks and dictionary of
# cohort size for each individual week
population_df, cohort_size = create_population_df("output/")
# Create timeseries of pulse oximetry codes usage for each region
region_list = [
    "North East",
    "North West",
    "Yorkshire and the Humber",
    "East Midlands",
    "West Midlands",
    "East of England",
    "London",
    "South East",
    "South West",
]

# Create data frame of sum totals for each index date for each oximetry code
oximetry_sum_regions = population_df.groupby(["index_date", "region"], as_index=False)[
    list(oximetry_headers_dict.keys())
].sum()

# Rename oximetry headers in oximetry sums data frame
oximetry_sum_regions.rename(columns=oximetry_headers_dict, inplace=True)

# Apply redaction to entire data frame
#oximetry_sum_regions = redact_and_round_df(oximetry_sum_regions)
# Apply further redaction to each oximetry column in turn
for header in list(oximetry_headers_dict.values()):
    #oximetry_sum_regions = further_redaction(oximetry_sum_regions, header)
    oximetry_sum_regions = redact_to_five_and_round(oximetry_sum_regions, header)

# For each region
for region in region_list:
    # Extract all rows for that region
    region_df = oximetry_sum_regions.loc[oximetry_sum_regions["region"] == region]
    # Save the dataframe in outputs folder
    region_df.to_csv("output/table_oximetry_counts_" + region + ".csv")
    # Create timeseries of pulse oximetry codes usage
    plt.figure(figsize=(20, 10))
    plt.rcParams.update({"font.size": 20})
    for column in oximetry_headers_dict.values():
        # Plot each line, skipping any non-numeric values
        plt.plot(
            region_df["index_date"], pd.to_numeric(region_df[column], errors="coerce")
        )
    plt.legend(
        list(oximetry_headers_dict.values()),
        loc="upper left",
        bbox_to_anchor=(1.0, 1.0),
        fontsize=20,
    )
    plt.xlabel("Date", fontsize=25)
    plt.title("Use of Pulse Oximetry Codes Over Time in " + region + " Region", fontsize=40)
    plt.savefig(
        "output/plot_oximetry_timeseries_region_" + region, bbox_inches="tight"
    )
