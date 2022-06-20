from typing import Dict, List
import random

from cohortextractor import codelist, patients


def make_variable(code: str, index_date: str, time: str, system: str) -> Dict[str, any]:

    if time == "between":
        return {
            f"healthcare_at_home_{code}": (
                patients.with_these_clinical_events(
                    codelist([code], system=system),
                    find_first_match_in_period=True,
                    returning="binary_flag",
                    between=[index_date, f"{index_date} + 6 days"],
                    return_expectations={"incidence": random.randint(1, 5) / 10},
                )
            )
        }

    if time == "on_or_before":
        return {
            f"healthcare_at_home_{code}": (
                patients.with_these_clinical_events(
                    codelist([code], system=system),
                    find_first_match_in_period=True,
                    returning="binary_flag",
                    on_or_before="index_date",
                    return_expectations={"incidence": random.randint(1, 5) / 10},
                )
            )
        }


def loop_over_codes(
    code_list: List, index_date: str, time: str = "between", system: str = "snomed"
):
    variables = {}
    for code in code_list:
        variables.update(make_variable(code, index_date, time, system))
    return variables
