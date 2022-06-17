# Script to find index dates for patient in "bp" cohort without a "bp" SNOMED code

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import bp_headers_dict, no_codes_used


homecare_type = "bp"
headers_dict = bp_headers_dict

no_codes_used(homecare_type)
