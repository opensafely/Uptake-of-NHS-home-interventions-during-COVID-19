from typing import Dict
import pandas as pd
import os
import math
import numpy as np
import matplotlib.pyplot as plt
from textwrap import wrap
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")
from analysis.analysis_data_processing.redaction import *
from analysis.codelist import oximetry_codes_dict, bp_codes_dict, proactive_codes_dict


def create_headers_dict(homecare_type: str) -> Dict:
    """Function to create header dictionary for the given homecare type,
    whose keys are the headers in input csv files (i.e. healthcare_at_home_code)
    and values are the terms they refer to"""
    # Find correct codes dictionary
    codes_dict_name = f"{homecare_type}_codes_dict"
    codes_dict = globals()[codes_dict_name]
    # Convert codes to headers used in population dataframe
    headers_dict = {f"healthcare_at_home_{k}": v for k, v in codes_dict.items()}
    return headers_dict


def create_population_df(homecare_type: str, dir: str) -> pd.DataFrame:
    """Function to create population data frame for a particular homecare type
    which includes all weeks and create a dictionary of cohort size for each
    individual week"""
    # find the input csv files
    filepaths = [
        f
        for f in os.listdir(dir)
        if (f.startswith(f"input_{homecare_type}") and f.endswith(".csv"))
    ]
    # append the directory path to filename
    filepaths_dir = [dir + filepath for filepath in filepaths]

    # create empty list to append dataframes
    dfs = []

    for file in filepaths_dir:
        # read in files
        output = pd.read_csv(file)
        # Add the index date to the file by extracting index from filename
        output["index_date"] = pd.to_datetime(
            file.split("_",)[4].split(
                ".csv"
            )[0],
            dayfirst=True,
        )
        # Append the dataframes to the list
        dfs.append(output)

    # Combine all the dataframes together
    population_df = pd.concat(dfs)

    # Rename the headers
    headers_dict = create_headers_dict(homecare_type)
    population_df.rename(columns=headers_dict, inplace=True)

    return population_df

def homecare_type_dir(homecare_type: str) -> Dict[str, str]:
    """Function to return a dictionary containing the input directory
    (location of the relevant input csv files) and output directory (where to
    store the analysis outputs) for a specific homecare type"""
    return dict(
        input_dir=f"output/{homecare_type}/0.2_join_cohorts/",
        output_dir=f"output/{homecare_type}/0.3_analysis_outputs/",
    )
