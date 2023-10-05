import cv2
import os
from pathlib import Path
from collections import namedtuple

import pandas as pd
import numpy as np
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
        raise Exception("No video streams found in file '{}'".format(video_path))

    # retrieve the first stream of type 'video'
    info_video = video_streams[0]

    video_w = info_video['width']
    video_h = info_video['height']
    n_frames = int(info_video['nb_frames'])

    return video_w, video_h, n_frames


VideoInfo = namedtuple("VideoInfo", ["width", "height", "n_frames", "fps", "codec"])


def extract_video_info(video_path: str) -> VideoInfo:
    """
    Uses the ffmpeg.probe function to retrieve information about a video file.

    :param video_path: Path to a valid video file
    :return: An instance of a VideoInfo named tuple with self-explaining information.
    """

    #
    # Fetch video info
    info = ffmpeg.probe(video_path)
    # Get the list of all video streams
    video_streams = [stream for stream in info['streams'] if stream['codec_type'] == 'video']
    if len(video_streams) == 0:
        raise Exception("No video streams found in file '{}'".format(video_path))

    # retrieve the first stream of type 'video'
    info_video = video_streams[0]

    framerate_ratio_str = info_video['r_frame_rate']
    fps = eval(framerate_ratio_str)

    out = VideoInfo(
        width=info_video['width'],
        height=info_video['height'],
        n_frames=int(info_video['nb_frames']),
        fps=fps,
        codec=info_video['codec_name']
    )

    return out


def extract_frames(video_file: str, timestamps_df: pd.DataFrame, output_dir: str) -> None:

    # Open the video file
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        raise Exception(f"Couldn't open video file '{video_file}'")

    first_col_name = timestamps_df.columns[0]
    timestamps: pd.Series = timestamps_df[first_col_name]

    # Loop over each timestamp in the CSV file
    for fnum, timestamp in enumerate(timestamps):
        # Extract the next frame
        ret, frame = cap.read()
        if ret:
            frame_path = os.path.join(output_dir, str(timestamp) + ".jpg")
            cv2.imwrite(frame_path, frame)

        else:
            print(f"At frame {fnum}, no more frames to extract from video '{video_file}'. Expected {len(timestamps)} frames.")

    # Release the video file
    cap.release()


def extract_frames_ffmpeg(video_file: str, timestamps_df: pd.DataFrame, output_dir: str) -> None:
    video_w, video_h, _ = video_info(video_file)

    ffmpeg_read_process = (
        ffmpeg
        .input(video_file)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .run_async(pipe_stdout=True)
    )

    first_col_name = timestamps_df.columns[0]
    timestamps: pd.Series = timestamps_df[first_col_name]

    # Loop over each timestamp in the CSV file
    for fnum, timestamp in enumerate(timestamps):
        in_bytes = ffmpeg_read_process.stdout.read(video_w * video_h * 3)
        if in_bytes:

            in_frame = (
                np
                .frombuffer(in_bytes, np.uint8)
                .reshape([video_h, video_w, 3])
            )

            frame_path = os.path.join(output_dir, str(timestamp) + ".jpg")
            in_frame = cv2.cvtColor(in_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(frame_path, in_frame)
            # PIL.Image.fromarray(in_frame, 'RGB').save(frame_path)

        else:
            print(f"At frame {fnum}, no more frames to extract from video '{video_file}'. Expected {len(timestamps)} frames.")

    if ffmpeg_read_process is not None:
        ffmpeg_read_process.stdout.close()
        ffmpeg_read_process.wait()
        ffmpeg_read_process = None


def rebuild_video(dir: Path, frames: pd.DataFrame, video_info: VideoInfo, outfile: Path, duplicate_last: bool = False)\
        -> None:

    """
    Given the directory containing unpacked frames and the dataframe, rebuilds a new video at teh given path.
    :param dir: The directory containing the single frames. Each frame with name specified in the frames dadaframe
    :param frames: A dataframe with two columns: `timestamp` is the name of the frame to append to the video,
     and `generated` can be either `Original` (file should be loaded) or `Generated` (insert a black frame or duplicate last).
    :param video_info: Anticipated info regarding the resolution of the output video.
     Resolution must match the resolution of input frame images.
    :param outfile: Path to the video output file.
    :param duplicate_last: If False (default) a black frame is inserted whenever a `Generated` frame is found.
     When True, the last valid frame is duplicated.
    :return: Nothing
    """

    # Extract the vido information.
    frame_width = video_info.width
    frame_height = video_info.height
    fps = video_info.fps

    font_width = int(frame_height * 0.04)

    # Initialize the ffmpeg encoder
    ffmpeg_video_out_process = (
        ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(frame_width, frame_height))
            .filter('fps', fps=fps)
            # -vf "drawtext=fontfile=Arial.ttf: fontsize=48: text=%{n}: x=(w-tw)/2: y=h-(2*lh): fontcolor=white: box=1: boxcolor=0x00000099"
            .drawtext(text="%{n}", escape_text=False,
                      # x=50, y=50,
                      x="(w-tw)/2", y="h-(2*lh)",
                      fontfile="Arial.ttf", fontsize=font_width, fontcolor="white",
                      box=1, boxborderw=2, boxcolor="Black@0.6")

            .output(str(outfile), pix_fmt='yuv420p')

            .overwrite_output()
            .run_async(pipe_stdin=True)
    )

    assert frame_width is not None and frame_height is not None and ffmpeg_video_out_process is not None

    # Initialize data for "Generated" frames
    black_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
    last_frame = black_frame

    #
    # Cycle through all the frames.
    for idx, row in frames.iterrows():
        ts = row["timestamp"]
        gen = row["generated"]

        if gen == "Original":

            frame_path = dir / (str(ts) + ".jpg")

            if not frame_path.exists():
                print(f"Skipping frame {str(frame_path)}")
                continue            # BEWARE! Continues the cycle

            img_bgr = cv2.imread(str(frame_path))
            img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

            img_height, img_width, _ = img.shape

            if img_height != frame_height or img_width != frame_width:
                raise Exception(f"The dimension of the read image ({img_width}x{img_height})"
                                f" does not match the dimension of the generated video {frame_width}x{frame_height}.")

            # Send the frame to the ffmpeg process
            ffmpeg_video_out_process.stdin.write(img.tobytes())

            last_frame = img

        elif gen == "Generated":

            if duplicate_last:
                pass
                print("Duplicating last valid frame")
                ffmpeg_video_out_process.stdin.write(last_frame.tobytes())
            else:
                # Create an artificial black frame
                print(f"Injecting Black frame at idx {idx}")
                ffmpeg_video_out_process.stdin.write(black_frame.tobytes())

        else:
            raise Exception(f"Unexpected value '{gen}' in column 'generated' at index {idx}")

    # Close the video stream
    if ffmpeg_video_out_process is not None:
        ffmpeg_video_out_process.stdin.close()
        ffmpeg_video_out_process.wait()
        ffmpeg_video_out_process = None
