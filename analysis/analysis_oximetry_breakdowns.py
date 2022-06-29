# Script to create timeseries plots for oximetry codes of
# interest broken down by variables of interest

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.analysis_breakdowns import analysis_breakdowns
from analysis.codelist import pulse_oximetry_codes


homecare_type = "oximetry"

analysis_breakdowns(homecare_type, pulse_oximetry_codes)
