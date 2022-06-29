# Script to create timeseries plots for proactive care codes of
# interest broken down by variables of interest

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.analysis_breakdowns import analysis_breakdowns
from analysis.codelist import proactive_codes


homecare_type = "proactive"
codes_of_interest = proactive_codes

analysis_breakdowns(homecare_type, codes_of_interest)
