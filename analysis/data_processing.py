from typing import Dict, List
import random

from cohortextractor import codelist, patients


def make_variable(code: str, index_date: str) -> Dict[str, any]:
    return {
        f"pulse_oximetry_{code}": (
            patients.with_these_clinical_events(
                codelist([code], system="snomed"),
                find_first_match_in_period=True,
                returning="binary_flag",
                between=[index_date, f"{index_date} + 7 days"],
                return_expectations={"incidence": random.randint(1,5)/10}
            )
        )
    }


def loop_over_codes(code_list: List, index_date: str):
    variables = {}
    for code in code_list:
        variables.update(make_variable(code, index_date))
    return variables
