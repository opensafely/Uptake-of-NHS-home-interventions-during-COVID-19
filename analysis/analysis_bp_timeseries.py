# Script to create timeseries of blood pressure monitoring codes usage

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.analysis_breakdowns import analysis_timeseries
from analysis.codelist import bp_codes

homecare_type = "bp"

analysis_timeseries(homecare_type, bp_codes)
