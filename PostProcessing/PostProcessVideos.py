import pandas as pd
import glob
import csv
import os
import cv2

import argparse

def compute_time_range(dfs):
    # Find the lowest and highest numbers in all the data frames
    min_common = max(df.iloc[:,0].min() for df in dfs)
    max_common = min(df.iloc[:,0].max() for df in dfs)

    # Print the results
    print(f"The lowest common number is {min_common}")
    print(f"The highest common number is {max_common}")
    
    return (min_common, max_common)


def trim_into_interval(csv_path, dfs, min_common, max_common):
    # Trim each data frame to the min_common and max_common interval and save to a new file
    for i, df in enumerate(dfs):
        df_trimmed = df[(df.iloc[:,0] >= min_common) & (df.iloc[:,0] <= max_common)]
        df_trimmed.to_csv(f"{csv_path}trimmed_df_{i+1}.csv", header=False, index=False)

    # Print the results
    print(f"{len(dfs)} data frames trimmed and saved to {csv_path}")


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



def main():

    # input_dir = "/Users/tbc/Desktop/videos/"
    # output_dir = "/Users/tbc/Desktop/output_videos/"
    # extract(input_dir, output_dir)
    # exit()
    # Define the path to the directory containing the CSV files
    csv_path = "/Users/tbc/Desktop/test_data/"

    # Find all CSV files in the directory
    csv_files = glob.glob(csv_path + "*.csv")

    # Create an empty list to hold the data frames
    dfs = []

    # Loop through each CSV file and read it into a data frame
    for file in csv_files:
        df = pd.read_csv(file, header=None)
        dfs.append(df)
    
    # Print total number of dataframes
    print(len(dfs))

    # Compute the time range
    min_common, max_common = compute_time_range(dfs)

    # Trim the data frames to the time range and save to new CSV files
    trim_into_interval(csv_path, dfs, min_common, max_common)


#
# MAIN
if __name__ == "__main__":
    pass

    # main()
    # exit(0)

    #
    # Find all CSV files in the directory and read it into a data frame (DONE)

    #
    # Find time ranges (Saurabh, To test better)

    #
    # Trim CSVs (TODO)

    #
    # Repair CSVs (TODO - Mina)

    #
    # Extract the frames from the original videos
    # and rename the file names to the timestamps (DONE)

    #
    # Reconstruct videos (TODO)
