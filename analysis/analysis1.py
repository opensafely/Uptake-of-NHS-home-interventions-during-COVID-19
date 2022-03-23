# Script to create timeseries of pulse oximetry codes usage

import pandas as pd
import matplotlib.pyplot as plt
import sys
# From .analysis_data_processing import create_population_df
if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import create_population_df

# Create population data frame which includes all weeks and dictionary of cohort size for each individual week
population_df, cohort_size = create_population_df("output/")

# Create lists of current and required headers
# Convert pulse oximetry codelist csv into data frame
oximetry_codes_df = pd.read_csv('codelists/opensafely-pulse-oximetry.csv')
# Extract list of SNOMED codes
oximetry_codes_list = oximetry_codes_df['code'].tolist()
# List of pulse oximetry headers in population dataframe
oximetry_codes_headers = [f'pulse_oximetry_{x}' for x in oximetry_codes_list]
# List of headers using descriptions as required
oximetry_headers = oximetry_codes_df['term'].tolist()

# Create dictionary for renaming oximetry headers
oximetry_dictionary = {}
for n in range(0,len(oximetry_codes_df)):
    oximetry_dictionary[oximetry_codes_headers[n]] = oximetry_headers[n]

# Create data frame of sum totals for each index date for each oximetry code
oximetry_sum = population_df.groupby(['index_date'], as_index=False)[oximetry_codes_headers].sum()
# Rename oximetry headers in oximetry sums data frame
oximetry_sum.rename(columns=oximetry_dictionary,inplace=True)
# Save the dataframe in outputs folder
oximetry_sum.to_csv('output/table_1_oximetry_counts.csv') 

# Create timeseries of pulse oximetry codes usage
plot_1 = oximetry_sum.plot.line('index_date',oximetry_headers, figsize=(20, 10), fontsize = 20).get_figure()
plt.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize = 20)
plt.xlabel("Date", fontsize = 25)
plt.title('Use of Pulse Oximetry Codes Over Time', fontsize = 40)
# Save plot in outputs folder
plot_1.savefig("output/plot_1_oximetry_timeseries.png", bbox_inches ="tight")