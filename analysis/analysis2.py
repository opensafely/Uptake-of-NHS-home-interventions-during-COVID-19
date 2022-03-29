# Script to create times series plot of the age categories

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import create_population_df, redact_and_round_column, redact_and_round_df

# Create population data frame which includes all weeks and dictionary of cohort size for each individual week
population_df, cohort_size = create_population_df("output/")

# Define the ranges for each of the age categories
# (e.g. [-1, 17] will find ages such that -1<age<=17 - age is a whole number in the data frame so this is anyone aged 0 to 17 inclusive)
age_bins = [-1, 17, 49, 64, 200]
n = len(age_bins)

# Create list of labels for the different age groups
age_group_labels = []
# For all except the last final age category the label is 'Age between ... and ...'
for i in range(0, len(age_bins)-2):
    age_group_labels.append(f'Age between {age_bins[i]+1} and {age_bins[i+1]+1}')
# For final age category the label is 'Age ... or over'
age_group_labels.append(f'Age {age_bins[-2]+1} or over')

# Create list of age category for each patient and insert into the population data frame
age_category = pd.cut(population_df.age, bins = age_bins, labels = age_group_labels)
population_df.insert(0, 'Age Group', age_category)


# Count the number of patients in each age group for each index date
age_counts = population_df.groupby(['index_date', 'Age Group']).size().reset_index()
age_counts.rename(columns={0: 'Counts'},inplace=True)

# Count the denominator (the total number of people) and use to obtain the percentage
age_counts['denominators'] = age_counts['index_date'].map(cohort_size) 
age_counts['percentage'] = age_counts['Counts'] / age_counts['denominators'] * 100
# Save the dataframe in outputs folder
age_counts.to_csv('output/table_2_age_counts.csv') 

# Plot the counts of the age groups over time (pivot to create separate columns for each age group)
plot_2_age = age_counts.pivot(index="index_date", columns="Age Group", values="percentage").plot(figsize=(20,10), fontsize = 20).get_figure()
plt.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize = 20)
plt.xlabel("Date", fontsize = 25)
plt.ylabel('Percentage of patients', fontsize = 25)
plt.title('Age groups of patients using pulse oximetry@ home over time', fontsize = 40)
plot_2_age.savefig("output/plot_2_age_timeseries.png", bbox_inches ="tight")