# Script to find index dates for patient in "oximetry" cohort without a "oximetry" SNOMED code

import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis_data_processing import oximetry_headers_dict, no_codes_used


homecare_type = "oximetry"
headers_dict = oximetry_headers_dict

no_codes_used(homecare_type)
