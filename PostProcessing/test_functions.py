import pytest

import os
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from dataframes import compute_time_step, scan_session_dir
from dataframes import repair_dropped_frames, compute_time_range

from video import video_info

from PostProcessVideos import DEFAULT_THRESHOLD_NANOS


RECSYNCH_SESSION_DIR_VAR = "RECSYNCH_SESSION_DIR"

print(f"Getting data dir from {RECSYNCH_SESSION_DIR_VAR} environment variable...")
RECSYNCH_SESSION_DIR = os.environ.get(RECSYNCH_SESSION_DIR_VAR)
print("Data root set at '{}'.".format(RECSYNCH_SESSION_DIR))


@pytest.fixture(scope="session", autouse=True)
def session_data() -> Tuple[List[str], List[pd.DataFrame], List[str]]:

    assert RECSYNCH_SESSION_DIR is not None, "Variable RECSYNCH_SESSION_DIR is None."
    assert os.path.exists(RECSYNCH_SESSION_DIR)
    assert os.path.isdir(RECSYNCH_SESSION_DIR)

    clienIDs, dataframes, video_paths = scan_session_dir(Path(RECSYNCH_SESSION_DIR))

    return clienIDs, dataframes, video_paths


def test_session_data(session_data):

    clienIDs, dataframes, video_paths = session_data

    assert len(clienIDs) > 0
    assert len(clienIDs) == len(dataframes) == len(video_paths)

    for df in dataframes:
        assert len(df) > 0
        assert len(df.columns) == 1

    for vp in video_paths:
        assert os.path.exists(vp)
        assert os.path.isfile(vp)

    for vp, df in zip(video_paths, dataframes):
        _, _, num_frames = video_info(vp)
        num_rows = len(df)
        # assert num_frames == num_rows, f"Num of frames in the video ({num_frames}) differs from the num of rows in the dataframe ({num_rows})."
        assert num_frames <= num_rows, f"Num of frames in the video ({num_frames}) is higher than the number of rows in the dataframe ({num_rows})."


def session_data_list() -> List[Tuple[str, pd.DataFrame, str]]:

    clienIDs, dataframes, video_paths = scan_session_dir(Path(RECSYNCH_SESSION_DIR))

    for clientID, df, video_path in zip(clienIDs, dataframes, video_paths):
        yield clientID, df, video_path


@pytest.mark.parametrize("client_data", session_data_list())
def test_df_reparation(client_data):

    _, df, _ = client_data
    assert len(df) >= 2

    first_col_name = df.columns[0]

    time_step = compute_time_step(df)
    assert time_step > 0

    repaired_df = repair_dropped_frames(df, time_step)

    assert len(repaired_df) > 2

    assert len(repaired_df) >= len(df), "Dataframe size was reduced after reparation."

    repaired_first_col_name = repaired_df.columns[0]
    repaired_second_col_name = repaired_df.columns[1]
    assert repaired_first_col_name == "timestamp"
    assert repaired_second_col_name == "generated"

    assert df[first_col_name].iloc[0] == repaired_df[repaired_first_col_name].iloc[0],\
        "The first element changed after reparation"
    assert df[first_col_name].iloc[-1] == repaired_df[repaired_first_col_name].iloc[-1],\
        "The last element changed after reparation"

    tstamps = repaired_df["timestamp"]
    diffs = tstamps.diff().dropna()
    assert (diffs <= (time_step + DEFAULT_THRESHOLD_NANOS)).all(), "some timestamps difference is longer than expected"


def test_df_trimming(session_data):
    _, dataframes, _ = session_data

    min_common, max_common = compute_time_range(dataframes)
    assert min_common <= max_common

    for df in dataframes:
        # Get the first element of the first column
        ts_start = df[0].iloc[0]
        assert ts_start <= min_common

        # Get the last element of the first column
        ts_end = df[0].iloc[-1]
        assert ts_end >= max_common


@pytest.mark.parametrize("client_data", session_data_list())
def test_video_sources(client_data):
    _, _, video_filepath = client_data

    video_path = Path(video_filepath)

    assert video_path.exists()
    assert video_path.is_file()

    w, h, n_frames = video_info(video_path)
    assert n_frames >= 2
