# Script to find index dates for patient in "proactive" cohort without a "proactive" SNOMED code

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import proactive_headers_dict, no_codes_used


homecare_type = "proactive"
headers_dict = proactive_headers_dict

no_codes_used(homecare_type)
