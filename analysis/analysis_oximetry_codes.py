# Script to create analysis tables of oximetry codes usage and combinations

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.codes_summary import code_analysis

homecare_type = "oximetry"

code_analysis(homecare_type)