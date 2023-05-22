import cv2
import os 

import pandas as pd
import ffmpeg

from typing import Tuple


def video_info(video_path: str) -> Tuple[int, int, int]:
    """
    Uses the ffmpeg.probe function to retrieve information about a video file.

    :param video_path: Path to a valid video file
    :return: A 3-tuple with integers for (width, height, number_of_frames)
    """

    #
    # Fetch video info
    info = ffmpeg.probe(video_path)
    # Get the list of all video streams
    video_streams = [stream for stream in info['streams'] if stream['codec_type'] == 'video']
    if len(video_streams) == 0:
        raise BaseException("No video streams found in file '{}'".format(video_path))

    # retrieve the first stream of type 'video'
    info_video = video_streams[0]

    video_w = info_video['width']
    video_h = info_video['height']
    n_frames = int(info_video['nb_frames'])

    return video_w, video_h, n_frames


def extract_frames(video_file: str, timestamps: pd.DataFrame, output_dir: str):

    # Open the video file
    cap = cv2.VideoCapture(video_file)
    assert cap.isOpened() == True
    video_name, _ = os.path.splitext(video_file)

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
