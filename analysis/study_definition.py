# Import from cohortextractor
from cohortextractor import StudyDefinition, codelist, patients

# Import codelist
from codelist import pulse_oximetry_codes, shielding_list


# Code to loop over pulse_oximetry to find the first match in the period
def loop_over_codes(code_list):
    def make_variable(code):
        return {
            f"pulse_oximetry_date_{code}": (
                patients.with_these_clinical_events(
                    codelist([code], system="snomed"),
                    on_or_after="index_date",
                    find_first_match_in_period=True,
                    returning="date",
                    date_format="YYYY-MM-DD",
                    return_expectations={
                        "incidence": 0.05,
                        "int": {"distribution": "normal",
                                "mean": 3,
                                "stddev": 1},
                    },
                )
            )
        }

    variables = {}
    for code in code_list:
        variables.update(make_variable(code))
    return variables


# Study definition
study = StudyDefinition(
    # Define default expectations
    default_expectations={
        "date": {"earliest": "index_date", "latest": "index_date + 7 days"},
        "incidence": "0.1",
    },
    # Define population
    population=patients.all(),
    # Set index date
    index_date="2021-01-01",
    # Sex
    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.49, "F": 0.51}},
        }
    ),
    # age
    age=patients.age_as_of(
        "index_date",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
            "incidence": 0.001,
        },
    ),
    # pulse oximetry date
    **loop_over_codes(pulse_oximetry_codes),
    # shielding
    shielding=patients.with_these_clinical_events(
        shielding_list,
        find_first_match_in_period=True,
        on_or_after="index_date",
        returning="binary_flag",
        return_expectations={
            "incidence": 0.1,
            "int": {"distribution": "normal", "mean": 3, "stddev": 1},
        },
    ),
    # index_of_multiple_deprivation
    index_of_multiple_deprivation=patients.address_as_of(
        date="index_date",
        returning="index_of_multiple_deprivation",
        round_to_nearest=100,
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"100": 0.1, "200": 0.2, "300": 0.7}},
        },
    ),
    # rural_urban_classification
    rural_urban_classification=patients.address_as_of(
        date="index_date",
        returning="rural_urban_classification",
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"rural": 0.3, "urban": 0.7}},
        },
    ),
)
