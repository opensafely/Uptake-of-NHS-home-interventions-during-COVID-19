from cohortextractor import codelist_from_csv, codelist

import pandas as pd
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")

# Codes dictionaries: Keys are SNOMED codes, values are the terms they refer to
# Create pulse oximetry dictionary
oximetry_codes_df = pd.read_csv("codelists/opensafely-pulse-oximetry.csv")
oximetry_codes_dict = oximetry_codes_df.set_index("code")["term"].to_dict()

# Pulse oximetry codes from OpenCodelists
pulse_oximetry_codes = codelist_from_csv(
    "codelists/opensafely-pulse-oximetry.csv", system="snomed", column="code"
)

# Blood pressure codes
bp_codes_dict = {
    413606001: "Average home systolic blood pressure",
    314446007: "Average day interval systolic blood pressure",
    413605002: "Average home diastolic blood pressure",
    314461008: "Average day interval diastolic blood pressure",
}

bp_codes = codelist([str(x) for x in list(bp_codes_dict.keys())], system="snomed")

# Proactive care code
proactive_codes_dict = {934231000000106: "Provision of proactive care"}
proactive_codes = codelist(
    [str(x) for x in list(proactive_codes_dict.keys())], system="snomed"
)

# Shielding list codes from OpenCodelists
shielding_list = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-shield.csv", system="snomed", column="code"
)

# Care home list
care_home_codes = codelist_from_csv(
    "codelists/opensafely-nhs-england-care-homes-residential-status.csv",
    system="snomed",
    column="code",
)

# COVID vaccination administration in EMIS
covid_vaccine_1_EMIS_codes = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-covadm1.csv",
    system="snomed",
    column="code",
)

covid_vaccine_2_EMIS_codes = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-covadm2.csv",
    system="snomed",
    column="code",
)

# Ethnicity list
# Using vaccine uptake ethnicty list
ethnicity_codelist = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth2001.csv",
    system="snomed",
    column="code",
    category_column="grouping_6_id",
)
# Alternative - use opensafely ethnicity list
ethnicity_codes = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    system="ctv3",
    column="Code",
    category_column="Grouping_6",
)

# Hypertension
hypertension_codes = codelist_from_csv(
    "codelists/opensafely-hypertension-snomed.csv",
    system="snomed",
    column="id",
)

# diabetes_type_2
diabetes_type_2_codes = codelist_from_csv(
    "codelists/opensafely-type-2-diabetes.csv",
    system="ctv3",
    column="CTV3ID",
)

# # asthma
asthma_codes = codelist_from_csv(
    "codelists/opensafely-asthma-diagnosis.csv",
    system="ctv3",
    column="CTV3ID",
)

# COPD
copd_codes = codelist_from_csv(
    "codelists/opensafely-current-copd.csv",
    system="ctv3",
    column="CTV3ID",
)

# Atrial fibrillation
atrial_fibrillation_codes = codelist_from_csv(
    "codelists/opensafely-atrial-fibrillation-or-flutter.csv",
    system="ctv3",
    column="CTV3Code",
)

# Cholesterol
cholesterol_codes = codelist_from_csv(
    "codelists/opensafely-cholesterol-tests-numerical-value.csv",
    system="snomed",
    column="code",
)
