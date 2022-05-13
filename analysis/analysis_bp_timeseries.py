# Script to create timeseries of blood pressure monitoring codes usage

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import bp_headers_dict
from analysis_functions import analysis_timeseries

homecare_type = "bp"
headers_dict = bp_headers_dict

analysis_timeseries(homecare_type, headers_dict)
