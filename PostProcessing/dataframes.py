import pandas as pd
import numpy as np

from typing import Tuple

THRESHOLD_NS = 10 * 1000 * 1000  # 10 milisecond


def compute_time_step(video_timestamps: pd.DataFrame) -> float:
    """
    Compute the time steps of a video based on its timestamps.

    Parameters:
    video_timestamps (pd.DataFrame): A pandas DataFrame containing timestamps of a video.

    Returns:
    float: The time step of the video time stamps.
    """

    first_col_name = video_timestamps.columns[0]
    time_step = (video_timestamps[first_col_name].diff()).dropna().value_counts().index[0]

    return time_step


def repair_dropped_frames(df: pd.DataFrame,  time_step: float) -> pd.DataFrame:

    first_col_name = df.columns[0]

    df[first_col_name] = pd.to_datetime(df[first_col_name]).astype(np.int64)
    timestamps = df[first_col_name]
    repaired_rows = []

    # Check for missing timestamps and generate them
    for i in range(len(timestamps) - 1):
        timestamp = timestamps.iloc[i]
        next_timestamp = timestamps.iloc[i + 1]

        repaired_rows.append([timestamp, 'Original'])

        if next_timestamp - timestamp > time_step:
            missing_timestamps_count = int((next_timestamp - timestamp)/ time_step) - 1
            interval = (next_timestamp - timestamp) / (missing_timestamps_count + 1)

            for j in range(1, missing_timestamps_count + 1):
                new_timestamp = (timestamp + j * interval).astype(np.int64)
                repaired_rows.append([new_timestamp, 'Generated'])

    # Add the last row
    repaired_rows.append([timestamps.iloc[-1], 'Original'])

    print(len(repaired_rows))
    # Create a new DataFrame with repaired rows
    columns = ['timestamp', 'generated']
    output_df = pd.DataFrame(repaired_rows, columns=columns)
    output_df['timestamp'] = pd.to_datetime(output_df['timestamp']).astype(np.int64)

    return output_df


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
