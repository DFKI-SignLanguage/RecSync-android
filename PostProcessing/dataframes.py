import pandas as pd

from typing import Tuple


def repair_dropped_frames(df: pd.DataFrame) -> pd.DataFrame:
    return df

def save_dataframes(dataframes, prefix='df'):
    # Generate filenames based on a pattern or numbering scheme
    filenames = [f"{prefix}{i}.csv" for i in range(1, len(dataframes) + 1)]

    # Save each DataFrame to a separate file
    for i, df in enumerate(dataframes):
        filename = filenames[i]
        df.to_csv(filename, index=False, header=False)
    print("DataFrames saved successfully.")


# Function to find the largest value in the first entry of all dataframes
def find_largest_first_entry(dfs):
    largest_value = float('-inf')
    for df in dfs:
        first_entry = df.iloc[0, 0]
        if first_entry > largest_value:
            largest_value = first_entry
    return largest_value


# Function to find the smallest value in the last entry of selected dataframes
def find_smallest_last_entry(dfs):
    smallest_value = float('inf')
    for df in dfs:
        last_entry = df.iloc[-1, 0]
        if last_entry < smallest_value:
            smallest_value = last_entry
    return smallest_value


# Function to find the largest & smallest value in the first and last entry of dataframes
def compute_time_range(dfs) -> Tuple[int, int]:
    # Find the lowest and highest numbers in all the data frames
    lower_value = find_largest_first_entry(dfs)
    higher_value = find_smallest_last_entry(dfs)

    # return the results
    return lower_value, higher_value


# Function to trim dataframes based on specified values
def trim_into_interval(dfs, min_common, max_common, threshold):
    trimmed_dataframes = []
    for df in dfs:
        start: pd.DataFrame = df[df.iloc[:, 0].between(min_common-threshold, min_common+threshold, inclusive='both')]
        end: pd.DataFrame = df[df.iloc[:, 0].between(max_common-threshold, max_common+threshold, inclusive='both')]
        if not start.empty and not end.empty :
            df_start = start.stack().iloc[0]
            df_end = end.stack().iloc[-1]
            trimmed_df = df[df.iloc[:, 0].between(df_start, df_end, inclusive='both')]
            trimmed_dataframes.append(trimmed_df)
        else:
            print("No values found within the specified range.")
    return trimmed_dataframes
