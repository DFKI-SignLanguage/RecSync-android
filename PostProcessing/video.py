import cv2
import os 

import pandas as pd

def extract_frames(video_file: str, timestamps: pd.DataFrame, output_dir: str):
    # Open the video file
    cap = cv2.VideoCapture(video_file)
    assert cap.isOpened() == True
    video_name = os.path.splitext(video_file)[0]
    # Loop over each timestamp in the CSV file
    for timestamp in timestamps:
        # Extract the frame using OpenCV
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ret, frame = cap.read()
        if ret:
            frame_name = f"{video_name}_{timestamp:.3f}.jpg"
            frame_path = os.path.join(output_dir, frame_name)
            cv2.imwrite(frame_path, frame)
    
    # Release the video file
    cap.release()
            
