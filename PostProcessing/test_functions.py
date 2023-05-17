import pytest

import os
from pathlib import Path

from typing import List, Tuple

from dataframes import repair_dropped_frames, compute_time_range
from PostProcessVideos import scan_session_dir

import pandas as pd

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


def session_data_list() -> List[Tuple[str, pd.DataFrame, str]]:

    clienIDs, dataframes, video_paths = scan_session_dir(Path(RECSYNCH_SESSION_DIR))

    for clientID, df, video_path in zip(clienIDs, dataframes, video_paths):
        yield (clientID, df, video_path)


def client_IDs() -> List[Path]:

    out = []

    for p in Path(RECSYNCH_SESSION_DIR).iterdir():
        print("-->", p.stem)
        out.append(p)

    return out


def CSVs() -> List[str]:

    out = []

    clients = client_IDs()
    for c in clients:
        client_dir = Path(RECSYNCH_SESSION_DIR) / c
        for csv_file in client_dir.glob("*.csv"):
            print("==>", csv_file)
            rel_filepath = str(csv_file.relative_to(RECSYNCH_SESSION_DIR))
            print("++>", rel_filepath)
            out.append(rel_filepath)

    return out


# @pytest.mark.parametrize("csv_file", CSVs())
# def test_df_reparation(csv_file):
#
#     # Load the test dataframes
#     csv_path = Path(RECSYNCH_SESSION_DIR) / csv_file
#     df = pd.read_csv(csv_path)
#
#     assert len(df) >= 2
#
#     repaired_df = repair_dropped_frames(df)
#
#     assert len(repaired_df) >= len(df)

@pytest.mark.parametrize("client_data", session_data_list())
def test_df_reparation(client_data):

    _, df, _ = client_data

    assert len(df) >= 2

    repaired_df = repair_dropped_frames(df)

    assert len(repaired_df) >= len(df)
    assert df[0].iloc[0] == repaired_df[0].iloc[0]
    assert df[0].iloc[-1] == repaired_df[0].iloc[-1]


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
