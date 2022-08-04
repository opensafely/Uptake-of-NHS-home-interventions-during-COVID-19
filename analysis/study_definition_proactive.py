# Import from cohortextractor
from cohortextractor import StudyDefinition, patients

# Import variables
from data_processing import loop_over_codes
from common_variables import common_variables


# Import codelist
from codelist import proactive_codes

from data_processing import loop_over_codes


# Study definition
study = StudyDefinition(
    # set index_date
    index_date="2019-04-01",
    # Define default expectations
    default_expectations={
        "date": {"earliest": "2019-04-01", "latest": "2022-02-01"},
        "incidence": "1",
        "rate": "uniform",
    },
    # Define population inclusion criteria
    population=patients.satisfying(
        """
            (has_proactive_code) AND
            (age > 0 AND age <= 120) AND
            (region != "") AND
            (imd_quintile != 0)
        """,
        has_proactive_code=patients.with_these_clinical_events(
            proactive_codes, between=["index_date", "index_date + 6 days"]
        ),
    ),
    # proactive care date
    # Code to loop over proactive_codes to find the first match in the period
    **loop_over_codes(
        proactive_codes, "index_date", returning="number_of_matches_in_period"
    ),
    # Loop over the common variables
    **common_variables
)
