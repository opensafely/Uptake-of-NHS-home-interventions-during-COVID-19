# Script to create timeseries of pulse oximetry codes usage for each region

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.analysis_breakdowns import analysis_region
from analysis.codelist import pulse_oximetry_codes

homecare_type = "oximetry"

analysis_region(homecare_type, pulse_oximetry_codes)
