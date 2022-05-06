# Import from cohortextractor
from cohortextractor import StudyDefinition, patients

# Import codelist
from codelist import (
    pulse_oximetry_codes,
    shielding_list,
    covid_vaccine_1_EMIS_codes,
    covid_vaccine_2_EMIS_codes,
    care_home_codes,
    ethnicity_codelist
)

from data_processing import loop_over_codes


# Study definition
study = StudyDefinition(
    # set index_date
    index_date="2021-01-01",
    # Define default expectations
    default_expectations={
        "date": {"earliest": "2019-04-01", "latest": "2022-02-01"},
        "incidence": "0.2",
        "rate": "uniform",
    },
    # Define population - anyone who recieved at least one pulse_oximetry_code on or after 2019-04-01
    population=patients.with_these_clinical_events(
        pulse_oximetry_codes, on_or_after="2019-04-01"
    ),
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
            "incidence": 1,
        },
    ),
    # pulse oximetry date
    # Code to loop over pulse_oximetry to find the first match in the period
    **loop_over_codes(pulse_oximetry_codes, "index_date"),
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
            "Not known": "DEFAULT",
            "1": """index_of_multiple_deprivation >=1 AND index_of_multiple_deprivation < 32844*1/5""",
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
                    "Not known": 0.01,
                    "1": 0.10,
                    "2": 0.20,
                    "3": 0.20,
                    "4": 0.30,
                    "5": 0.19,
                }
            },
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
    # Covid vaccination 1
    covid_vax_1_date=patients.with_vaccination_record(
        returning="date",
        tpp={
            "target_disease_matches": "SARS-2 CORONAVIRUS",
        },
        emis={
            "procedure_codes": covid_vaccine_1_EMIS_codes,
        },
        find_first_match_in_period=True,
        on_or_before="index_date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2020-12-08",
                "latest": "2022-02-01",
            },
            "incidence": 0.9,
        },
    ),
    # Covid vaccination 2
    covid_vax_2_date=patients.with_vaccination_record(
        returning="date",
        tpp={
            "target_disease_matches": "SARS-2 CORONAVIRUS",
        },
        emis={
            "procedure_codes": covid_vaccine_2_EMIS_codes,
        },
        find_first_match_in_period=True,
        between=["covid_vax_1_date + 15 days", "index_date"],
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2020-12-31",
                "latest": "2022-02-01",
            },
            "incidence": 0.9,
        },
    ),
    # Covid vaccination 3
    covid_vax_3_date=patients.with_vaccination_record(
        returning="date",
        tpp={
            "target_disease_matches": "SARS-2 CORONAVIRUS",
        },
        emis={
            "procedure_codes": covid_vaccine_2_EMIS_codes,
        },
        find_first_match_in_period=True,
        between=["covid_vax_2_date + 15 days", "index_date"],
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2020-01-15",
                "latest": "2022-02-01",
            },
            "incidence": 0.7,
        },
    ),
    # Covid test result in the index week
    covid_positive_test_date=patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        returning="binary_flag",
        between=["index_date", "index_date + 7 days"],
        find_first_match_in_period=True,
        restrict_to_earliest_specimen_date=False,
        return_expectations={
            "date": {
                "earliest": "2020-12-31",
                "latest": "2022-02-01",
            },
            "incidence": 0.5,
        },
    ),
    # Ethnicity
    ethnicity=patients.categorised_as(
        {
            "Missing": "DEFAULT",
            "White": "eth='1' OR (NOT eth AND ethnicity_sus='1')",
            "Mixed": "eth='2' OR (NOT eth AND ethnicity_sus='2')",
            "South Asian": "eth='3' OR (NOT eth AND ethnicity_sus='3')",
            "Black": "eth='4' OR (NOT eth AND ethnicity_sus='4')",
            "Other": "eth='5' OR (NOT eth AND ethnicity_sus='5')",
        },
        return_expectations={
            "category": {
                "ratios": {
                    "White": 0.2,
                    "Mixed": 0.2,
                    "South Asian": 0.2,
                    "Black": 0.2,
                    "Other": 0.2,
                }
            },
            "incidence": 0.4,
        },
        ethnicity_sus=patients.with_ethnicity_from_sus(
            returning="group_6",
            use_most_frequent_code=True,
            return_expectations={
                "category": {
                    "ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}
                },
                "incidence": 0.4,
            },
        ),
        eth=patients.with_these_clinical_events(
            ethnicity_codelist,
            returning="category",
            find_last_match_in_period=True,
            on_or_before="index_date",
            return_expectations={
                "category": {
                    "ratios": {"1": 0.4, "2": 0.4, "3": 0.2, "4": 0.2, "5": 0.2}
                },
                "incidence": 0.75,
            },
        ),
    ),
)
