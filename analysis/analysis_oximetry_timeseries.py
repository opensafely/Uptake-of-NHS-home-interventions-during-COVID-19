# Script to create timeseries of oximetry codes usage

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.analysis_breakdowns import analysis_timeseries

homecare_type = "oximetry"

analysis_timeseries(homecare_type)
