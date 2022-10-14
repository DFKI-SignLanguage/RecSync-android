import argparse
import pandas

parser = argparse.ArgumentParser(
    description="Rebuilds a video given the unpacked frames (with timetamp name) and the match CSV file."
)
parser.add_argument("--csv", help="the CSV resulting from MATCH", required=True)
parser.add_argument("--frames", help="the directory containing the frames", required=True)
parser.add_argument("--output", "-o", help="The output video file", required=True)

# TODO

