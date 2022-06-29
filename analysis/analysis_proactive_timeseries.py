# Script to create timeseries of proactive care codes usage

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.analysis_breakdowns import analysis_timeseries

homecare_type = "proactive"

analysis_timeseries(homecare_type)
