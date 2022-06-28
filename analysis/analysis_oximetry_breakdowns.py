# Script to create timeseries plots for oximetry codes of
# interest broken down by variables of interest

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import oximetry_codes_dict
from analysis_functions import analysis_breakdowns


homecare_type = "oximetry"
codes_dict = oximetry_codes_dict
codes_of_interest = ["1325191000000108", "1325221000000101", "1325241000000108"]

analysis_breakdowns(homecare_type, codes_dict, codes_of_interest)
