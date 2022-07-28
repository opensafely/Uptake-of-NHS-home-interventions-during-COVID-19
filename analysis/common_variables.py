from cohortextractor import patients

from codelist import *
from data_processing import loop_over_codes

common_variables = dict(
    # sex
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
            "incidence": 1,
        },
    ),
    # shielding
    shielding=patients.with_these_clinical_events(
        shielding_list,
        find_first_match_in_period=True,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.1},
    ),
    # care home
    care_home=patients.with_these_clinical_events(
        care_home_codes,
        find_first_match_in_period=True,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.25},
    ),
    # IMD quintile
    imd_quintile=patients.categorised_as(
        {
            "0": "DEFAULT",
            "1": """index_of_multiple_deprivation >=0 AND index_of_multiple_deprivation < 32844*1/5""",
            "2": """index_of_multiple_deprivation >= 32844*1/5 AND index_of_multiple_deprivation < 32844*2/5""",
            "3": """index_of_multiple_deprivation >= 32844*2/5 AND index_of_multiple_deprivation < 32844*3/5""",
            "4": """index_of_multiple_deprivation >= 32844*3/5 AND index_of_multiple_deprivation < 32844*4/5""",
            "5": """index_of_multiple_deprivation >= 32844*4/5 """,
        },
        index_of_multiple_deprivation=patients.address_as_of(
            date="index_date",
            returning="index_of_multiple_deprivation",
            round_to_nearest=100,
        ),
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0": 0.01,
                    "1": 0.10,
                    "2": 0.20,
                    "3": 0.20,
                    "4": 0.30,
                    "5": 0.19,
                }
            },
        },
    ),
    # region the patient lives in
    region=patients.registered_practice_as_of(
        "2020-02-01",
        returning="nuts1_region_name",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "North East": 0.1,
                    "North West": 0.1,
                    "Yorkshire and the Humber": 0.1,
                    "East Midlands": 0.1,
                    "West Midlands": 0.1,
                    "East of England": 0.1,
                    "London": 0.2,
                    "South East": 0.1,
                    "South West": 0.1,
                },
            },
        },
    ),
    # Patient has hypertension
    has_hypertension_code=patients.with_these_clinical_events(
        hypertension_codes,
        on_or_before="index_date",
        returning ="binary_flag",
        return_expectations={
            "date": {
                "earliest": "2020-01-15",
                "latest": "2022-02-01",
            },
            "incidence": 0.7,
        },
    ),
    # Patient has diabetes type 2
    has_diabetes_type_2_code=patients.with_these_clinical_events(
        diabetes_type_2_codes,
        on_or_before="index_date",
        returning ="binary_flag",
        return_expectations={
            "date": {
                "earliest": "2020-01-15",
                "latest": "2022-02-01",
            },
            "incidence": 0.7,
        },
    ),
    # Asthma
    has_asthma_code=patients.with_these_clinical_events(
        asthma_codes,
        on_or_before="index_date",
        returning ="binary_flag",
        return_expectations={
            "date": {
                "earliest": "2020-01-15",
                "latest": "2022-02-01",
            },
            "incidence": 0.7,
        },
    ),
    # COPD
    has_copd_code=patients.with_these_clinical_events(
        copd_codes,
        on_or_before="index_date",
        returning ="binary_flag",
        return_expectations={
            "date": {
                "earliest": "2020-01-15",
                "latest": "2022-02-01",
            },
            "incidence": 0.7,
        },
    ),
    # atrial-fibrillation
    has_atrial_fibrillation_code=patients.with_these_clinical_events(
        atrial_fibrillation_codes,
        on_or_before="index_date",
        returning ="binary_flag",
        return_expectations={
            "date": {
                "earliest": "2020-01-15",
                "latest": "2022-02-01",
            },
            "incidence": 0.7,
        },
    ),
    # Cholesterol
    **loop_over_codes(cholesterol_codes, "index_date", "cholesterol", returning="numeric_value")
)
