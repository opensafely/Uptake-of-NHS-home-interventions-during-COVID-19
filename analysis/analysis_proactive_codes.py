# Script to create analysis tables of proactive codes usage and combinations

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.codes_summary import code_analysis
from analysis.codelist import proactive_codes

homecare_type = "proactive"

code_analysis(homecare_type, proactive_codes)
