# Script to create times series plot for breakdowns by age category, shielding status, sex, IMD decile, ethnicity and care home residency

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple
import math
from textwrap import wrap
import sys
if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import create_population_df, redact_and_round_column, redact_and_round_df, code_specific_analysis


# Create population data frame which includes all weeks and dictionary of cohort size for each individual week
population_df, cohort_size = create_population_df("output/")

# Create dictionary of oximetry codes and terms they refer to
oximetry_codes_df = pd.read_csv('codelists/opensafely-pulse-oximetry.csv')
oximetry_codes_dict = oximetry_codes_df.set_index("code")["term"].to_dict()

# Define the ranges for each of the age categories
# (e.g. [-1, 39] will find ages such that -1<age<=39 - age is a whole number in the data frame so this is anyone aged 0 to 40 inclusive)
age_bins = [-1, 39, 49, 64, 200]
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
population_df.insert(0, 'age_group', age_category)

# Add IMD Decile column
population_df['IMD_decile'] = (population_df['index_of_multiple_deprivation']/328.44 * 10).apply(np.ceil).astype(int)


# Create timeseries for each of the variables

# Define which oximetry codes to create timeseries breakdowns for
codes_of_interest = ['1325191000000108', '1325221000000101', '1325241000000108']

# Create timeseries for oximetry codes broken down by sex
for code in codes_of_interest:
    code_specific_analysis(code, 'sex', population_df, oximetry_codes_dict)
    legend_handles, legend_labels = plt.gca().get_legend_handles_labels()
    new_labels = {'F': 'Female', 'M': 'Male'}
    for i in range(0, len(legend_labels)):
        legend_labels[i] = new_labels[legend_labels[i]]
    plt.legend(legend_labels, loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize = 20)
    plt.savefig("output/timeseries/plot_" + code + "_" + "sex" + "_timeseries.png", bbox_inches ="tight")

# Create timeseries for oximetry codes broken down by care_home
for code in codes_of_interest:
    code_specific_analysis(code, 'care_home', population_df, oximetry_codes_dict)
    legend_handles, legend_labels = plt.gca().get_legend_handles_labels()
    new_labels = {'0': 'Not a care home resident', '1': 'Care home resident'}
    for i in range(0, len(legend_labels)):
        legend_labels[i] = new_labels[legend_labels[i]]
    plt.legend(legend_labels, loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize = 20)
    plt.title('\n'.join(wrap('Patients with \"' + oximetry_codes_dict[int(code)] + '\" code,\n grouped by ' + 'care home residency')), fontsize = 40)
    plt.savefig("output/timeseries/plot_" + code + "_" + "care_home" + "_timeseries.png", bbox_inches ="tight")

# Create timeseries for oximetry codes broken down by ethnicity_6_sus
for code in codes_of_interest:
    code_specific_analysis(code, 'ethnicity_6_sus', population_df, oximetry_codes_dict)
    plt.title('\n'.join(wrap('Patients with \"' + oximetry_codes_dict[int(code)] + '\" code,\n grouped by ' + 'ethnicity')), fontsize = 40)
    plt.savefig("output/timeseries/plot_" + code + "_" + "ethnicity_6_sus" + "_timeseries.png", bbox_inches ="tight")

# Create timeseries for oximetry codes broken down by IMD
for code in codes_of_interest:
    code_specific_analysis(code, 'IMD_decile', population_df, oximetry_codes_dict)
    plt.title('\n'.join(wrap('Patients with \"' + oximetry_codes_dict[int(code)] + '\" code,\n grouped by ' + 'IMD decile (1 = most deprived, 10 = least deprived)')), fontsize = 40)
    plt.savefig("output/timeseries/plot_" + code + "_" + "IMD_decile" + "_timeseries.png", bbox_inches ="tight")

# Create timeseries for oximetry codes broken down by age group
for code in codes_of_interest:
    code_specific_analysis(code, 'age_group', population_df, oximetry_codes_dict)
    plt.title('\n'.join(wrap('Patients with \"' + oximetry_codes_dict[int(code)] + '\" code,\n grouped by ' + 'age')), fontsize = 40)
    plt.savefig("output/timeseries/plot_" + code + "_" + "age_group" + "_timeseries.png", bbox_inches ="tight")

# Create timeseries for oximetry codes broken down by shielding status
for code in codes_of_interest:
    code_specific_analysis(code, 'shielding', population_df, oximetry_codes_dict)
    legend_handles, legend_labels = plt.gca().get_legend_handles_labels()
    new_labels = {'0': 'Not shielding', '1': 'Shielding'}
    for i in range(0, len(legend_labels)):
        legend_labels[i] = new_labels[legend_labels[i]]
    plt.legend(legend_labels, loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize = 20)
    plt.title('\n'.join(wrap('Patients with \"' + oximetry_codes_dict[int(code)] + '\" code,\n grouped by ' + 'shielding status')), fontsize = 40)
    plt.savefig("output/timeseries/plot_" + code + "_" + "shielding" + "_timeseries.png", bbox_inches ="tight")
