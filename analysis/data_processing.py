from typing import Dict, List
import random

from cohortextractor import codelist, patients


def make_variable(code: str, index_date: str, title: str, returning: str) -> Dict[str, any]:
    
    if returning == "binary_flag":
        return_expectations = {"incidence": random.randint(1, 5) / 10}

    if returning == "numeric_value":
        return_expectations = {
            "float": {"distribution": "normal", "mean": 45.0, "stddev": 20},
            "incidence": 0.5,
        }

    
    return {
        f"{title}_{code}": (
            patients.with_these_clinical_events(
                codelist([code], system="snomed"),
                find_first_match_in_period=True,
                returning=returning,
                ignore_missing_values=True,
                between=[index_date, f"{index_date} + 6 days"],
                return_expectations=return_expectations,
            )
        )
    }


def loop_over_codes(
    code_list: List, index_date: str, title: str = "healthcare_at_home", returning: str = "binary_flag"
) -> Dict[str, any]:
    variables = {}
    for code in code_list:
        variables.update(make_variable(code, index_date, title, returning))
    return variables
