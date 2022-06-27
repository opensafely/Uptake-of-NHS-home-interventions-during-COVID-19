import pandas as pd
import math


def redact_and_round_column(column: pd.Series) -> pd.Series:
    """Function which takes a column of data, redacts any values less than or
    equal to 5 and rounds all other values up to nearest 5"""
    # New column variable will contain the new values with any necessary
    # redacting and rounding applied
    new_column = []
    # For loop to apply redacting and rounding to all integer or float values
    # in the column
    for value in column:
        if type(value) == int or type(value) == float:
            # Redact values less than or equal to 5
            if value <= 5:
                value = "[REDACTED]"
            # Round all values greater than 5 up to nearest 5
            else:
                value = int(5 * math.ceil(float(value) / 5))
        # Resulting value is added to the new column
        new_column.append(value)
    return new_column
    

def redact_and_round_df(df: pd.DataFrame) -> pd.DataFrame:
    """Function to take a dataframe, redact any values less than or equal to 5 and
    round all other values up to nearest 5"""
    # Apply redacting and rounding to each column of the dataframe
    for column in df.columns.values:
        df[column] = redact_and_round_column(df[column])
    return df


def redact_to_five_and_round(
    counts_df: pd.DataFrame, column_to_redact: str
) -> pd.DataFrame:
    """Function which determines for each index date if any value in a dataframe column
    is <= 5 and if so redacts all values <=5 then continues redacting the next lowest
    value until the redacted values add up to >= 5.
    All remaining values are then rounded up to nearest 5"""
    # For each index date
    for index_date in counts_df.index_date.unique():
        # Create temporary dataframe of all the rows with that index date
        temp_df = counts_df[counts_df["index_date"] == index_date]
        # If sum of values in the column <= 5
        if pd.to_numeric(temp_df[column_to_redact], errors="coerce").sum() <= 5:
            # Redact all values in the column
            temp_df[column_to_redact] = "[REDACTED]"
        # Else if there are any numbers <= 5 in the column of interest
        elif (
            pd.to_numeric(
                temp_df[column_to_redact][
                    pd.to_numeric(temp_df[column_to_redact], errors="coerce") <= 5
                ],
                errors="coerce",
            ).count()
            > 0
        ):
            # Store total quantity redacted
            total_redacted = 0
            # For each row
            for index in temp_df.index.values:
                # If column value is less than 5
                if (
                    pd.to_numeric(temp_df.loc[index, column_to_redact], errors="coerce")
                    <= 5
                ):
                    # Add to the total_redacted variable
                    total_redacted += temp_df.loc[index, column_to_redact]
                    # Redact the value
                    temp_df.loc[index, column_to_redact] = "[REDACTED]"
                    # While total_redacted <= 5
                    while total_redacted <= 5:
                        # Find index of the lowest non-redacted count for that index date
                        min_index = pd.to_numeric(
                            temp_df[temp_df[column_to_redact] != "[REDACTED]"][
                                column_to_redact
                            ]
                        ).idxmin()
                        # Add to the total_redacted variable
                        total_redacted += temp_df.loc[min_index, column_to_redact]
                        # Redact the value
                        temp_df.at[min_index, column_to_redact] = "[REDACTED]"
        # Update counts dataframe with the redactions
        counts_df.update(temp_df)
    # Round all numeric values in column up to nearest 5
    for index in counts_df.index.values:
        value = counts_df.loc[index, column_to_redact]
        if type(value) != str:
            counts_df.loc[index, column_to_redact] = int(
                5 * math.ceil(float(value) / 5)
            )
    return counts_df


def further_redaction_all(counts_df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Function which takes a dataframe countaining a column of counts and
    redacts all counts for an index date if any one of the counts for that
    date is already redacted"""
    # For  each row of the dataframe
    for index, row in counts_df.iterrows():
        # If count redacted
        if row[column_name] == "[REDACTED]":
            # Find  its index date
            removal_index = row["index_date"]
            # Redact counts for all rows with that index date
            counts_df.loc[
                counts_df["index_date"] == removal_index, column_name
            ] = "[REDACTED]"
    return counts_df


def further_redaction(counts_df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Function which takes a dataframe and redacts smallest remaining value
    in a column for each index date, if one value in that column is already
    redacted for that index date"""
    # For each index date
    for index_date in counts_df.index_date.unique():
        # Create temporary dataframe of all the rows with that index date
        temp_df = counts_df[counts_df["index_date"] == index_date]
        # Count how many are redacted
        number_of_redactions = temp_df[column_name].to_list().count("[REDACTED]")
        # If one count is redacted
        if number_of_redactions == 1:
            # Find index of the lowest non-redacted count for that index date
            min_index = pd.to_numeric(
                temp_df[temp_df[column_name] != "[REDACTED]"][column_name]
            ).idxmin()
            # Redact it
            temp_df.at[min_index, column_name] = "[REDACTED]"
            # Update counts dataframe with extra redaction
            counts_df.update(temp_df)
    return counts_df

