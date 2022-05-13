# Script to create timeseries of proactive care codes usage

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import proactive_headers_dict
from analysis_functions import analysis_timeseries

homecare_type = "proactive"
headers_dict = proactive_headers_dict

analysis_timeseries(homecare_type, headers_dict)
