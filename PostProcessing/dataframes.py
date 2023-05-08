import pandas as pd


def repair_dropped_frames(df: pd.DataFrame) -> pd.DataFrame:
    pass


def compute_time_range(dfs):
    # Find the lowest and highest numbers in all the data frames
    min_common = max(df.iloc[:,0].min() for df in dfs)
    max_common = min(df.iloc[:,0].max() for df in dfs)

    # Print the results
    print(f"The lowest common number is {min_common}")
    print(f"The highest common number is {max_common}")

    return (min_common, max_common)


def trim_into_interval(csv_path, dfs, min_common, max_common):
    # Trim each data frame to the min_common and max_common interval and save to a new file
    for i, df in enumerate(dfs):
        df_trimmed = df[(df.iloc[:,0] >= min_common) & (df.iloc[:,0] <= max_common)]
        df_trimmed.to_csv(f"{csv_path}trimmed_df_{i+1}.csv", header=False, index=False)

    # Print the results
    print(f"{len(dfs)} data frames trimmed and saved to {csv_path}")
