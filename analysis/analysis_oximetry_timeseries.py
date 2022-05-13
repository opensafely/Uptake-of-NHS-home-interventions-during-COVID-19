# Script to create timeseries of pulse oximetry codes usage

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import oximetry_headers_dict
from analysis_functions import analysis_timeseries

homecare_type = "oximetry"
headers_dict = oximetry_headers_dict

analysis_timeseries(homecare_type, headers_dict)
