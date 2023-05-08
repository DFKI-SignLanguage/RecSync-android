import os
import csv
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

import pandas as pd
import cv2

from dataframes import compute_time_range, trim_into_interval, repair_dropped_frames


THRESHOLD_NS = 10 * 1000 * 1000


def extract(input_dir, output_dir):
    # Loop over each directory in the input directory
    for dir_name in os.listdir(input_dir):
        dir_path = os.path.join(input_dir, dir_name)
        if os.path.isdir(dir_path):
            # Find the video file in the directory
            video_filename = None
            for filename in os.listdir(dir_path):
                if filename.endswith(".mp4"):
                    video_filename = filename
                    break
            if video_filename is None:
                continue
            
            # Define the path to the input video
            input_path = os.path.join(dir_path, video_filename)
            
            # Find the CSV file in the directory
            csv_filename = os.path.splitext(video_filename)[0] + ".csv"
            csv_path = os.path.join(dir_path, csv_filename)
            
            # Read the CSV file with the timestamps
            timestamps = []
            with open(csv_path, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    timestamps.append(float(row[0]))
            
            # Define the output directory for the frames
            video_name = os.path.splitext(video_filename)[0]
            video_output_dir = os.path.join(output_dir, dir_name)
            if not os.path.exists(video_output_dir):
                os.makedirs(video_output_dir)
            
            # Open the video file
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                continue
            
            # Loop over each timestamp in the CSV file
            for timestamp in timestamps:
                # Extract the frame using OpenCV
                cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
                ret, frame = cap.read()
                if ret:
                    frame_name = f"{video_name}_{timestamp:.3f}.jpg"
                    frame_path = os.path.join(video_output_dir, frame_name)
                    cv2.imwrite(frame_path, frame)
            
            # Release the video file
            cap.release()



def main(input_dir: Path, output_dir: Path):

    # input_dir = Path("/Users/tbc/Desktop/videos/")
    # output_dir = Path("/Users/tbc/Desktop/output_videos/")

    #
    # Find all CSV files in the directory and read it into a data frame (DONE)

    #
    clientIDs: List[str] = []
    for p in input_dir.iterdir():
        print("Found client -->", p.stem)
        # TODO -- we could also check if the ClientID complies to the numerical format (using regex).
        clientIDs.append(p.stem)

    # Will be filled with key=clientID:str, data=Tuple[csv:DataFrame, videofile:str]
    clients_data: Dict[str, Tuple[pd.DataFrame, str]] = dict()

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
        mp4_file = MP4s[1]

        df: pd.DataFrame = pd.read_csv(csv_file, header=None)

        clients_data[cID] = (df, str(mp4_file))


    # Define the path to the directory containing the CSV files
    # csv_path = "/Users/tbc/Desktop/test_data/"

    #
    # Repair CSVs (TODO - Mina)
    repaired_client_data = dict()
    for cID, (df, mp4) in clients_data:
        repaired_df = repair_dropped_frames(df)
        repaired_client_data[cID] = repaired_df, mp4

    #
    # Find time ranges (Saurabh, To test better)
    # Compute the time range
    dfs = [df for k, (df, _) in clients_data]
    min_common, max_common = compute_time_range(dfs)

    #
    # Trim CSVs (TODO)
    # Trim the data frames to the time range and save to new CSV files
    csv_path = output_dir / "test"
    # TODO -- actually, we don't need to save them. We could just return them as DataFrame instances
    trim_into_interval(csv_path, dfs, min_common, max_common)


    #
    # Extract the frames from the original videos
    # and rename the file names to the timestamps (DONE)
    # extract(input_dir, output_dir)


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
        "--infolder", type=str, help="The folder containing the collected videos and CSV files with the timestamps.",
        required=True
    )
    parser.add_argument(
        "--outfolder", type=str, help="The folder where the repaired and aligned frames will be stored.",
        required=True
    )

    args = parser.parse_args()

    infolder = Path(args.infolder)
    outfolder = Path(args.outfolder)

    if not infolder.exists():
        raise Exception(f"Input folder '{infolder}' doesn't exist.")

    if not infolder.exists():
        raise Exception(f"Output folder '{outfolder}' doesn't exist.")

    main(infolder, outfolder)
