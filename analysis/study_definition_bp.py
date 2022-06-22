# Import from cohortextractor
from cohortextractor import StudyDefinition, patients

# Import variables
from data_processing import loop_over_codes
from common_variables import common_variables

# Import codelist
from codelist import bp_codes


# Study definition
study = StudyDefinition(
    # set index_date
    index_date="2019-04-01",
    # Define default expectations
    default_expectations={
        "date": {"earliest": "2019-04-01", "latest": "2022-02-01"},
        "incidence": "0.2",
        "rate": "uniform",
    },
    # Define population inclusion criteria
    population=patients.satisfying(
        """
            (has_bp_code) AND
            (age > 0 AND age <= 120) AND
            (region != "") AND
            (imd_quintile != 0)
        """,
        has_bp_code=patients.with_these_clinical_events(
            bp_codes, between=["2019-04-01", "2022-06-05"], ignore_missing_values=True
        ),
    ),
    # blood pressure monitoring date
    # Code to loop over bp_codes to find the first match in the period
    **loop_over_codes(bp_codes, "index_date"),
    # Loop over the common variables
    **common_variables
)
