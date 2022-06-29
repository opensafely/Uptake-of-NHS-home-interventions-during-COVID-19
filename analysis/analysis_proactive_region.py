# Script to create timeseries of proactive care codes usage for each region

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.analysis_breakdowns import analysis_region
from analysis.codelist import proactive_codes

homecare_type = "proactive"

analysis_region(homecare_type, proactive_codes)
