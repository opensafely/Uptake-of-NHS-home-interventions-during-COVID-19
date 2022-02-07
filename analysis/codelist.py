from cohortextractor import codelist_from_csv

# Pulse oximetry codes from OpenCodelists
pulse_oximetry_codes = codelist_from_csv(
    "codelists/opensafely-pulse-oximetry.csv", system="snomed", column="code"
)
# Add shielding list
# Shielding list codes from OpenCodelists
shielding_list = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-shield.csv", system="snomed",
    column="code")

# First COVID vaccination administration in EMIS
covid_vaccine_EMIS_codes = codelist_from_csv(
  "codelists/primis-covid19-vacc-uptake-covadm1.csv",
  system="snomed",
  column="code",
)
