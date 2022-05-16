# Script to create timeseries of pulse oximetry codes usage for each region

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import bp_headers_dict
from analysis_functions import code_analysis

homecare_type = "bp"
headers_dict = bp_headers_dict

code_analysis(homecare_type, headers_dict)
