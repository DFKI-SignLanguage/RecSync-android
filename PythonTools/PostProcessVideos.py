import argparse
from pathlib import Path
from typing import List
import tempfile

import pandas as pd

from dataframes import compute_time_range, trim_repaired_into_interval, scan_session_dir
from dataframes import repair_dropped_frames, compute_time_step

from video import extract_frames
from video import rebuild_video
from video import extract_video_info


DEFAULT_THRESHOLD_MILLIS = 10
DEFAULT_THRESHOLD_NANOS = DEFAULT_THRESHOLD_MILLIS * 1000 * 1000  # millis * micros * nanos


#
#
#
def post_process(input_dir: Path, output_dir: Path, threshold_ns: int = DEFAULT_THRESHOLD_NANOS):

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
        print(f"Client ID {cID} repaired from {len(df)} to {len(repaired_df)} frames")

    assert len(clientIDs) == len(df_list) == len(mp4_list) == len(repaired_df_list)

    #
    # Trim CSVs
    # Find time ranges
    min_common, max_common = compute_time_range(repaired_df_list)
    # Trim the data frames to the time range
    trimmed_dataframes = trim_repaired_into_interval(repaired_df_list, min_common, max_common, threshold_ns)

    assert len(clientIDs) == len(trimmed_dataframes), f"Expected {len(clientIDs)} trimmed dataframes. Found f{len(trimmed_dataframes)}"

    #
    # Check if the number of frames in the dataframe matches with the timestamps between last and first entry
    for cID, df in zip(clientIDs, trimmed_dataframes):
        diff_info = df['timestamp'].diff().dropna().value_counts()
        # print(diff_info)
        estimated_step = diff_info.index[0]
        first_ts = df['timestamp'].iloc[0]
        last_ts = df['timestamp'].iloc[-1]
        time_diff = last_ts - first_ts
        # print(f"first/last timestamps: {first_ts}/{last_ts}. Diff={time_diff}")
        estimated_frames = (time_diff / estimated_step) + 1
        print(f"cID {cID}. Size={len(df)}. Diff={time_diff}. Estimated frames={estimated_frames}.")

    #
    # Check that all the resulting dataframes have the same number of rows
    print("Checking if all clients we have the same number of frames in the repaired-and-trimmed tables...")
    client0ID = clientIDs[0]
    client0size = len(trimmed_dataframes[0])
    print(f"Client {client0ID} has {client0size} frames.")
    for cID, df in zip(clientIDs[1:], trimmed_dataframes[1:]):
        dfsize = len(df)
        if client0size != dfsize:
            raise Exception(f"For client {cID}: expecting {client0size} frames. Found {dfsize}."
                            f" This might be due to an excessive phase offset during recording."
                            f" Try to increase the threshold.")

    print("Good. All trimmed dataframes have the same number of entries.")

    #
    # Unpack the original videos, and repack them according to repaired and trimmed dataframes.
    for i, cID in enumerate(clientIDs):
        orig_df = df_list[i]
        trimmed_df = trimmed_dataframes[i]
        video_file = mp4_list[i]
        # Create a temporary directory for frames unpacking
        with tempfile.TemporaryDirectory(prefix="RecSyncNG", suffix=cID) as tmp_dir:
            # Extract the frames from the original videos
            # and rename the file names to the timestamps
            print(f"Extracting {len(orig_df)} frames from '{video_file}'...")
            extract_frames(video_file=video_file, timestamps_df=orig_df, output_dir=tmp_dir)

            # Reconstruct videos
            vinfo = extract_video_info(video_path=video_file)
            video_out_filepath = output_dir / (cID + ".mp4")
            rebuild_video(dir=Path(tmp_dir), frames=trimmed_df, video_info=vinfo, outfile=video_out_filepath)
            # And save also the CSV
            csv_out_filepath = video_out_filepath.with_suffix(".csv")
            trimmed_df.to_csv(path_or_buf=csv_out_filepath, header=True, index=False)


#
# MAIN
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Fixes the videos produced by the RecSync recording sessions."
                    "Converts the input recorder videos into videos with the same number of frames,"
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
    parser.add_argument(
        "--create-outfolder", "-co", action="store_true", help="If the output folder doesn't exist, tries to create it.",
        required=True
    )
    parser.add_argument(
        "--threshold", "-t", type=int, help="The allowed difference in ms between corresponding frames on different videos."
                                            " Increase this is post processing fails with trimmed tables of different sizes."
                                            f" Default is now {DEFAULT_THRESHOLD_MILLIS} ms.",
        required=False,
        default=DEFAULT_THRESHOLD_MILLIS
    )

    args = parser.parse_args()

    infolder = Path(args.infolder)
    outfolder = Path(args.outfolder)
    create_outfolder = args.create_outfolder
    threshold_millis = args.threshold
    threshold_nanos = threshold_millis * 1000 * 1000

    if not infolder.exists():
        raise Exception(f"Input folder '{infolder}' doesn't exist.")

    if not outfolder.exists():
        if create_outfolder:
            outfolder.mkdir(parents=True, exist_ok=True)
        else:
            raise Exception(f"Output folder '{outfolder}' doesn't exist.")

    post_process(input_dir=infolder, output_dir=outfolder, threshold_ns=threshold_nanos)
