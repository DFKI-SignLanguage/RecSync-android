import argparse
from pathlib import Path
import subprocess
import math

from video import video_info

from typing import List, Tuple

# See https://ffmpeg.org/ffmpeg-filters.html#xstack-1 for documentation on the xstack filter
# Example (assuming HD input videos):
"""
ffmpeg -y -i video1.mp4 \
-i video2.mp4 \
-i video3.mp4 \
-filter_complex \
"\
[0:v]scale=w=960:h=540[v0]; \
[1:v]scale=w=960:h=540[v1]; \
[2:v]scale=w=960:h=540[v2]; \
[v0][v1][v2]xstack=inputs=3:layout=0_0|960_0|0_540[v]\
" \
-map "[v]" \
finalOutput.mp4
"""


def create_video_grid_collage(video_files: List[str], output_file: str, grid_size: Tuple[int, int]) -> None:
    # Determine the dimensions of each grid cell
    grid_width, grid_height = grid_size
    input_width, input_height, _ = video_info(video_files[0])
    cell_width = input_width // grid_width
    cell_height = input_height // grid_height

    # Compose the ffmpeg command to create the collage
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
    ]

    # Set the list of input videos
    for i, video_file in enumerate(video_files):
        cmd.extend(["-i", video_file])

    #
    # Generate the ffmpeg filtergraph
    filtergraph = ""

    # First, created the scaled video instances
    for i, video_file in enumerate(video_files):
        filtergraph += f"[{i}:v]scale=w={cell_width}:h={cell_height}[v{i}];"

    # Now compose the layout for the xstack filter
    xscale_positions = []
    for i, video_file in enumerate(video_files):
        col = i % grid_width
        row = i // grid_width
        xscale_positions.append(f"{cell_width*col}_{cell_height*row}")

    filtergraph += "".join([f"[v{i}]" for i in range(len(video_files))])
    filtergraph += f"xstack=inputs={len(xscale_positions)}:layout="
    filtergraph += "|".join(xscale_positions)  # Compose the xstack layout (e.g.: "0_0|960_0|0_540")
    filtergraph += "[v]"

    # Append the complex filter and the remaining parameters
    cmd.extend([
        "-filter_complex", filtergraph,
        "-map", "[v]",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        output_file
    ])
    print("CMD:", cmd)
    subprocess.run(cmd, capture_output=False)


#
# MAIN
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Fixes the videos produced by the RecSync recording sessions."
                    "Converts the input recorder videos into videos with the same number of frames,"
                    "with missing/dropped frames inserted as (black) artificial data."
    )
    parser.add_argument(
        "--infolder", "-i", type=str, help="The folder containing the fixed videos.",
        required=True
    )
    parser.add_argument(
        "--outvideo", "-o", type=str, help="The filename to save the generated video.",
        required=True
    )

    args = parser.parse_args()

    input_dir = Path(args.infolder)
    out_filename = args.outvideo

    input_video_paths = input_dir.glob("*.mp4")
    video_list = [str(p) for p in input_video_paths]
    # print("Input videos: ", video_list)

    # Compute the most squared grid to contain the given number of input videos (drops a row if needed)
    n_videos = len(video_list)
    n_cols = math.ceil(math.sqrt(n_videos))
    n_rows = math.ceil(n_videos / n_cols)
    # print(f"Composing grid of (cols X rows): {n_cols}X{n_rows}")

    # Number of rows will be the same as number of columns, or one less
    assert n_rows * n_cols >= n_videos
    assert n_cols - 1 <= n_rows <= n_cols

    grid_size = (n_cols, n_rows)

    create_video_grid_collage(video_list, out_filename, grid_size)
