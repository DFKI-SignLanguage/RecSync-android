import pytest

import os
from pathlib import Path

from typing import List

from dataframes import repair_dropped_frames, compute_time_range, trim_into_interval

import pandas as pd

import pandas.testing as pd_testing

import numpy as np

RECSYNCH_SESSION_DIR_VAR = "RECSYNCH_SESSION_DIR"

print(f"Getting data dir from {RECSYNCH_SESSION_DIR_VAR} environment variable...")
RECSYNCH_SESSION_DIR = os.environ.get(RECSYNCH_SESSION_DIR_VAR)
print("Data root set at '{}'.".format(RECSYNCH_SESSION_DIR))

#@pytest.fixture(autouse=True)
#def client_dir() -> str:
#    if RECSYNCH_SESSION_DIR is None:
#        raise Exception(f"Environment variable {RECSYNCH_SESSION_DIR_VAR} not defined")


# def client_IDs() -> List[str]:

#     out = []

#     for p in Path(RECSYNCH_SESSION_DIR).iterdir():
#         print("-->", p.stem)
#         out.append(p)

#     return out


# def CSVs() -> List[str]:

#     out = []

#     clients = client_IDs()
#     for c in clients:
#         client_dir = Path(RECSYNCH_SESSION_DIR) / c
#         for csv_file in client_dir.glob("*.csv"):
#             print("==>", csv_file)
#             rel_filepath = str(csv_file.relative_to(RECSYNCH_SESSION_DIR))
#             print("++>", rel_filepath)
#             out.append(rel_filepath)

#     return out


# @pytest.mark.parametrize("csv_file", CSVs())
# def test_df_reparation(csv_file):

#     # Load the test dataframes
#     csv_path = Path(RECSYNCH_SESSION_DIR) / csv_file
#     df = pd.read_csv(csv_path)

#     assert len(df) >= 2

#     repaired_df = repair_dropped_frames(df)

#     assert len(repaired_df) >= len(df)


def test_df_trim():
    # Create three sample dataframes with single column and no headers
    df1 = pd.DataFrame([9, 10, 11, 16])
    df2 = pd.DataFrame([7, 8, 12, 13])
    df3 = pd.DataFrame([12, 15, 16, 19])

    # Add the dataframes to a list
    df_list = [df1, df2, df3]

    # Compute time range and trim the dataframe 
    min_val, max_val = compute_time_range(df_list)
    trimmed_df_list = trim_into_interval(df_list, min_val, max_val, 3)

    # Create expected list of dataframes to compare with trimmed_df_list
    compare_list = [
        pd.DataFrame([9, 10, 11, 16]),
        pd.DataFrame([12, 13]),
        pd.DataFrame([12, 15, 16])
    ]
    
    # print(trimmed_df_list.to_string(index=False))
    # print(compare_list.to_string(index=False))
    # try:
    #     for df1, df2 in zip(trimmed_df_list, compare_list):
    #         df1_reset = df1.reset_index(drop=True)
    #         df2_reset = df2.reset_index(drop=True)
    #         pd_testing.assert_frame_equal(df1_reset, df2_reset)
    #     print("All dataframes match")
    # except AssertionError as e:
    #     print("Dataframes do not match:")
    #     print(e)
    # Assert if all dataframes in df_list match the corresponding dataframes in compare_list
    assert trimmed_df_list == compare_list
