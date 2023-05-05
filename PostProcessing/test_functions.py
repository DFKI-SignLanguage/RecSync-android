

from dataframes import repair_dropped_frames


def test_df_reparation():

    # Load the test dataframes
    df = None

    repaired_df = repair_dropped_frames(df)

    assert len(repaired_df) >= len(df)
