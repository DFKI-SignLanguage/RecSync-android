import pandas as pd

from typing import Tuple


def repair_dropped_frames(df: pd.DataFrame) -> pd.DataFrame:
    return df


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
    # import pdb;pdb.set_trace()
    for df in dfs:
        start: pd.DataFrame = df[(df.iloc[:, 0] >= min_common - threshold) & (df.iloc[:, 0] <= min_common + threshold)]
        end: pd.DataFrame = df[(df.iloc[:, 0] >= max_common - threshold) & (df.iloc[:, 0] <= max_common + threshold)]
        trimmed_df = df[(df.iloc[:, 0] >= start.iloc[0, 0]) & (df.iloc[:, 0] <= end.iloc[0, 0])].reset_index(drop=True)
        trimmed_dataframes.append(trimmed_df)
    return trimmed_dataframes
