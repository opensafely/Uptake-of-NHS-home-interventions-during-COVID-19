# Script to create timeseries plots for blood pressure monitoring codes of
# interest broken down by variables of interest

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.analysis_breakdowns import analysis_breakdowns


homecare_type = "bp"
codes_of_interest = ["413606001"]

analysis_breakdowns(homecare_type, codes_of_interest)
