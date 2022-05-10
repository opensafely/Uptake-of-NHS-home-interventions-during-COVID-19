from cohortextractor import codelist_from_csv

# Pulse oximetry codes from OpenCodelists
pulse_oximetry_codes = codelist_from_csv(
    "codelists/opensafely-pulse-oximetry.csv", system="snomed", column="code"
)

# Blood pressure codes
bp_codes = codelist_from_csv(
    "codelists/blood-pressure.csv", system="snomed", column="code"
)

# Proactive care code
proactive_codes = codelist_from_csv(
    "codelists/proactive-care.csv", system="snomed", column="code"
)

# Shielding list codes from OpenCodelists
shielding_list = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-shield.csv", system="snomed", column="code"
)

# Care home list
care_home_codes = codelist_from_csv(
    "codelists/opensafely-nhs-england-care-homes-residential-status.csv", system="snomed", column="code"
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
    "codelists/opensafely-ethnicity.csv", system="ctv3", column="Code", category_column="Grouping_6",
)