# Script to create timeseries plots for blood pressure monitoring codes of
# interest broken down by variables of interest

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import bp_codes_dict
from analysis_functions import analysis_breakdowns


homecare_type = "bp"
codes_dict = bp_codes_dict
# Codes_of_interest is a list of blood pressure monitoring codes as strings
codes_of_interest = [str(x) for x in list(bp_codes_dict.keys())]

analysis_breakdowns(homecare_type, codes_dict, codes_of_interest)
