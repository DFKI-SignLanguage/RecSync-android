import pandas as pd
import numpy as np

from typing import Tuple, List


def compute_time_step(video_timestamps: pd.DataFrame) -> float:
    """
    Compute the time steps of a video based on its timestamps.

    Parameters:
    video_timestamps (pd.DataFrame): A pandas DataFrame containing timestamps of a video.

    Returns:
    float: The time step of the video time stamps.
    """

    first_col_name = video_timestamps.columns[0]
    # Retrieves the most frequent time different between consecutive lines.
    time_step = (video_timestamps[first_col_name].diff()).dropna().value_counts().index[0]

    return time_step


def repair_dropped_frames(df: pd.DataFrame, time_step: float) -> pd.DataFrame:
    # The name of the first column (can be anythign as the original df doesn't have header
    first_col_name = df.columns[0]

    # Forces the type of the timestamps to int64
    df[first_col_name] = pd.to_datetime(df[first_col_name]).astype(np.int64)
    # Retrieves the timestamps into a Series
    timestamps = df[first_col_name]
    # Will accumulate the repaired rows
    repaired_rows = []

    # Check for missing timestamps and generate them
    for i in range(len(timestamps) - 1):
        timestamp = timestamps.iloc[i]
        next_timestamp = timestamps.iloc[i + 1]

        # The current timestamp is by definition original
        repaired_rows.append([timestamp, 'Original'])

        # If the next timestamp exceeds the expected time step
        if next_timestamp - timestamp > time_step:
            # Estimate the number of missing frames
            missing_timestamps_count = round((next_timestamp - timestamp) / time_step) - 1
            # Estimate a time interval between them (will be very similar to the input time_step
            interval = (next_timestamp - timestamp) / (missing_timestamps_count + 1)
            # Generate the missing lines
            for j in range(1, missing_timestamps_count + 1):
                new_timestamp = (timestamp + j * interval).astype(np.int64)
                repaired_rows.append([new_timestamp, 'Generated'])

    # Add the last row
    repaired_rows.append([timestamps.iloc[-1], 'Original'])
    # print(len(repaired_rows))

    # Create a new DataFrame with repaired rows
    columns = ['timestamp', 'generated']
    output_df = pd.DataFrame(repaired_rows, columns=columns)
    # Forces the output timestamp type to int 64
    output_df['timestamp'] = pd.to_datetime(output_df['timestamp']).astype(np.int64)

    return output_df


def save_dataframes(dataframes, prefix='df') -> None:
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
def trim_repaired_into_interval(dfs, min_common, max_common, threshold) -> List[pd.DataFrame]:

    trimmed_dataframes: List[pd.DataFrame] = []

    lo_threshold = min_common - threshold
    hi_threshold = max_common + threshold

    for df in dfs:

        selection_mask = df["timestamp"].between(lo_threshold, hi_threshold, inclusive='both')
        trimmed_df = df[selection_mask]
        trimmed_dataframes.append(trimmed_df)

        assert len(trimmed_dataframes) <= len(df)

    return trimmed_dataframes