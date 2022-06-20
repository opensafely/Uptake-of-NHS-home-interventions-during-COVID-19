from cohortextractor import (
    StudyDefinition,
    patients,
)
from codelist import hypertension_codes
from data_processing import loop_over_codes

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "1980-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.05,
    },
    index_date="2022-06-05",
    population=patients.all(),
    **loop_over_codes(hypertension_codes, "index_date", time="on_or_before", system="ctv3"),
)
