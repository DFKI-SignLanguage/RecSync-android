import pytest

import os
from pathlib import Path

from typing import List

from dataframes import repair_dropped_frames

import pandas as pd

RECSYNCH_SESSION_DIR_VAR = "RECSYNCH_SESSION_DIR"

print(f"Getting data dir from {RECSYNCH_SESSION_DIR_VAR} environment variable...")
RECSYNCH_SESSION_DIR = os.environ.get(RECSYNCH_SESSION_DIR_VAR)
print("Data root set at '{}'.".format(RECSYNCH_SESSION_DIR))

#@pytest.fixture(autouse=True)
#def client_dir() -> str:
#    if RECSYNCH_SESSION_DIR is None:
#        raise Exception(f"Environment variable {RECSYNCH_SESSION_DIR_VAR} not defined")


def client_IDs() -> List[str]:

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


@pytest.mark.parametrize("csv_file", CSVs())
def test_df_reparation(csv_file):

    # Load the test dataframes
    csv_path = Path(RECSYNCH_SESSION_DIR) / csv_file
    df = pd.read_csv(csv_path)

    assert len(df) >= 2

    repaired_df = repair_dropped_frames(df)

    assert len(repaired_df) >= len(df)
