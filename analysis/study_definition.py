# Import from cohortextractor
from cohortextractor import (
    StudyDefinition,
    codelist,
    codelist_from_csv,
    combine_codelists,
    filter_codes_by_category,
    patients,
    Measure
)

# Import codelists
from codelists import *

#Study definition
study = StudyDefinition(

    # Define default expectations
    default_expectations={
        "date": {"earliest": "2019-04-01", "latest": "today"},
        "distribution": "poisson",
        "incidence": "0.1"
    },

    # Define population
    population=patients.with_these_clinical_events(pulse_oximetry_codes, between=["2019-04-01", "today"])
)
