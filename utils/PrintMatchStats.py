import argparse
import pandas


parser = argparse.ArgumentParser(
    description="Analyse match dataframe."
)
parser.add_argument(
    "--input", "-i", help="the CSV resulting from MATCH",
    required=True
)

args = parser.parse_args()

csv_file = args.input

df = pandas.read_csv(csv_file)

print("Number of entries", len(df))

print(df.dtypes)

print("\nDifferences between left and T")
left_t_diff = df.left - df.t
print("Mean:", left_t_diff.mean())
print("Std:", left_t_diff.std())
print("Max: ", left_t_diff.max())
print("Min: ", left_t_diff.min())


print("\nDifferences between right and T")
right_t_diff = df.right - df.t
print("Mean:", right_t_diff.mean())
print("Std:", right_t_diff.std())
print("Max: ", right_t_diff.max())
print("Min: ", right_t_diff.min())


print("\nTime difference between frames in left")
left_diff = df.left.diff()
print("Mean: ", left_diff.mean())
print("Std: ", left_diff.std())
print("Max: ", left_diff.max())
print("Min: ", left_diff.min())
print("Count: ", left_diff.value_counts())

print("\nTime difference between frames in right")
right_diff = df.right.diff()
print("Mean: ", right_diff.mean())
print("Std: ", right_diff.std())
print("Max: ", right_diff.max())
print("Min: ", right_diff.min())
print("Count: ", right_diff.value_counts())

