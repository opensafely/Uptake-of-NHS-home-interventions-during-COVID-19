# Import from cohortextractor
from cohortextractor import StudyDefinition, patients

# Import codelist
from codelist import (
    pulse_oximetry_codes,
    shielding_list,
    covid_vaccine_1_EMIS_codes,
    covid_vaccine_2_EMIS_codes,
    care_home_codes,
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
    population=patients.satisfying(
        """
            (has_oximetry_code) AND
            (age > 0 AND age <= 120) AND
            (region != "") AND
            (imd_quintile != 0)
        """,
        has_oximetry_code=patients.with_these_clinical_events(
            pulse_oximetry_codes,  between=["2022-02-07", "2022-04-17"]
        ),
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
    )
)
