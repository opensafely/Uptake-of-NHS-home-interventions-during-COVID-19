# Script to create analysis tables of oximetry codes usage and combinations

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import proactive_headers_dict
from analysis_functions import code_analysis

homecare_type = "proactive"
headers_dict = proactive_headers_dict

code_analysis(homecare_type, headers_dict)
