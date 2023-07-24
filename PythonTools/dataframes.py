import re
from pathlib import Path

import pandas as pd
import numpy as np

from typing import Tuple, List


def compute_time_step(video_timestamps: pd.DataFrame) -> float:
    """
    Compute the time steps of a video based on its timestamps.

    Parameters:
    video_timestamps (pd.DataFrame): A pandas DataFrame containing timestamps of a video.

    Returns:
    float: The time step of the video time stamps, in nanoseconds.
    """

    first_col_name = video_timestamps.columns[0]
    # Retrieves the most frequent time different between consecutive lines.
    time_step = (video_timestamps[first_col_name].diff()).dropna().value_counts().index[0]

    return time_step


def repair_dropped_frames(df: pd.DataFrame, time_step: float) -> pd.DataFrame:
    # The name of the first column (can be anythign as the original df doesn't have header
    first_col_name = df.columns[0]

    # Forces the type of the timestamps to int64
    df[first_col_name] = df[first_col_name].astype(np.int64)
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
    # output_df['timestamp'] = pd.to_datetime(output_df['timestamp']).astype(np.int64)

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


def scan_session_dir(input_dir: Path) -> Tuple[List[str], List[pd.DataFrame], List[str]]:
    """Used to scan a 'raw' directory, as downloaded from the remote controller.
    Finds all CSV and mp4 files in the all client directories and read return the lists of:
    the client IDs, the loaded dataframes, the paths to the videos files.
    All the three lists have the same number of elements.
    Raises an exception if is more than one video in a client directory: it means that more videos were recorded
    using the same session ID, and this must be manually cleaned up.
    """
    # Use the following regular expression to check of the client ID is a 16-digit hexadecimal.
    clientIDpattern = "[\\da-f]" * 16
    patt = re.compile("^" + clientIDpattern + "$")

    # Fill this list with the client IDs found n the directory
    clientIDs: List[str] = []
    for p in input_dir.iterdir():
        # Check if the ClientID complies to the numerical format (using regex).
        res = patt.match(p.stem)
        if res:
            # print("Found client -->", p.stem)
            clientIDs.append(p.stem)
        else:
            # print("Discarding ", p.stem)
            pass

    #
    # Accumulates the list of dataframes and mp4 files in the same order of the client IDs.
    df_list: List[pd.DataFrame] = []
    mp4_list: List[str] = []

    for cID in clientIDs:
        client_dir = input_dir / cID
        CSVs = list(client_dir.glob("*.csv"))
        MP4s = list(client_dir.glob("*.mp4"))
        #
        # Consistency check. Each clientID folder must have exactly 1 CSV and 1 mp4.
        if len(CSVs) != 1:
            raise Exception(f"Expecting 1 CSV file for client {cID}. Found {len(CSVs)}.")

        if len(MP4s) != 1:
            raise Exception(f"Expecting 1 MP4 file for client {cID}. Found {len(MP4s)}.")

        csv_file = CSVs[0]
        mp4_file = MP4s[0]

        df: pd.DataFrame = pd.read_csv(csv_file, header=None)

        df_list.append(df)
        mp4_list.append(str(mp4_file))

    return clientIDs, df_list, mp4_list