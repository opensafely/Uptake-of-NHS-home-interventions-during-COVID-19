# Import from cohortextractor
from cohortextractor import (
    StudyDefinition,
    codelist,
    patients,
)

# Import codelist
from codelist import *


# Flag if a code was used that week
# Return True if code was used that week and the date
def code_assigned_that_week(code):
    return {
        f"flag_{code}": patients.with_these_clinical_events(
            codelist([code], system="snomed"),
            between=["2019-04-01", "2019-04-07"],
            find_first_match_in_period=True,
            return_binary_flag=True,
            date_format="YYYY-MM-DD",
            return_expectations={
                "incidence": 0.1,
                "int": {"distribution": "normal", "mean": 3, "stddev": 1},
            },
        )
    }

# Loop over the codes for that week, so flags will appear for each code if True
def loop_over_codes(code_list):
    variables = {}
    for code in code_list:
        variables.update(code_assigned_that_week(code))
    return variables


# Study definition
study = StudyDefinition(
    # Define default expectations
    default_expectations={
        "date": {"earliest": "2019-04-01", "latest": "today"},
        "distribution": "poisson",
        "incidence": "0.1",
    },
    # Define population
    **loop_over_codes(pulse_oximetry_codes),
)
