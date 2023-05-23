import argparse
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import re

from dataframes import compute_time_range, trim_into_interval
from dataframes import repair_dropped_frames, compute_time_step

from video import extract_frames


THRESHOLD_NS = 10 * 1000 * 1000


def scan_session_dir(input_dir: Path) -> Tuple[List[str], List[pd.DataFrame], List[str]]:
    #
    # Find all CSV files in the directory and read it into a data frame
    # Use the following regular expression to check of the client ID is a 16-digit hexadecimal.
    clientIDpattern = "[\\da-f]" * 16
    patt = re.compile("^" + clientIDpattern + "$")

    # Fill this list with the client IDs found n the directory
    clientIDs: List[str] = []
    for p in input_dir.iterdir():
        # Check if the ClientID complies to the numerical format (using regex).
        res = patt.match(p.stem)
        if res:
            print("Found client -->", p.stem)
            clientIDs.append(p.stem)
        else:
            print("Discarding ", p.stem)

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


#
#
#
def main(input_dir: Path, output_dir: Path):

    print(f"Scanning dir {str(input_dir)}...")
    clientIDs, df_list, mp4_list = scan_session_dir(input_dir)

    n_clients = len(clientIDs)


    #
    # Print collected info
    for i in range(n_clients):
        cID = clientIDs[i]
        df = df_list[i]
        mp4 = mp4_list[i]
        print(f"For client ID {cID}: {len(df)} frames for file {mp4}")

    #
    # Repair CSVs
    repaired_df_list: List[pd.DataFrame] = []
    for cID, df in zip(clientIDs, df_list):
        time_step = compute_time_step(df)
        repaired_df = repair_dropped_frames(df=df, time_step=time_step)
        repaired_df_list.append(repaired_df)

    assert len(clientIDs) == len(df_list) == len(mp4_list) == len(repaired_df_list)

    #
    # Find time ranges
    # Compute the time range
    min_common, max_common = compute_time_range(repaired_df_list)

    #
    # Trim CSVs
    # Trim the data frames to the time range
    trimmed_dataframes = trim_into_interval(repaired_df_list, min_common, max_common, THRESHOLD_NS)

    assert len(clientIDs) == len(trimmed_dataframes), f"Expected {len(clientIDs)} trimmed dataframes. Found f{len(trimmed_dataframes)}"

    client0ID = clientIDs[0]
    client0size = len(trimmed_dataframes[0])
    print(f"For client {client0ID}: {client0size} frames")
    for cID, df in zip(clientIDs[1:], trimmed_dataframes[1:]):
        dfsize = len(df)
        if client0size != dfsize:
            raise Exception(f"For client {cID}: expecting {client0size}, found {dfsize}")

    print("Good. All trimmed dataframes have the same number of entries.")

    #
    # Extract the frames from the original videos
    # and rename the file names to the timestamps (DONE)
    # extract_frames(input_dir, output_dir)

    #
    # Reconstruct videos (TODO)


#
# MAIN
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Fixes the videos produced by the RecSync recording sessions."
                    "Output videos will have the same number of frames,"
                    "with missing/dropped frames inserted as (black) artificial data."
    )
    parser.add_argument(
        "--infolder", "-i", type=str, help="The folder containing the collected videos and CSV files with the timestamps.",
        required=True
    )
    parser.add_argument(
        "--outfolder", "-o", type=str, help="The folder where the repaired and aligned frames will be stored.",
        required=True
    )

    args = parser.parse_args()

    infolder = Path(args.infolder)
    outfolder = Path(args.outfolder)

    if not infolder.exists():
        raise Exception(f"Input folder '{infolder}' doesn't exist.")

    if not outfolder.exists():
        raise Exception(f"Output folder '{outfolder}' doesn't exist.")

    main(infolder, outfolder)
