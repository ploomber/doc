import pandas as pd
import sys

if __name__ == "__main__":
    if (len(sys.argv) != 2 or not sys.argv[1].endswith(".csv")):
        raise ValueError("Usage: python csv-clean.py filename.csv")
    
    in_file = sys.argv[1]
    df = pd.read_csv(in_file)

    # Clean out null values
    df = df[df['DEP_TIME'].notnull() & df['DEP_DELAY'].notnull()]

    # Ensure hour is between 0 and 23 for conversion
    df.loc[df.DEP_TIME == 2400, 'DEP_TIME'] = 0

    # Add time to date and convert
    df["DEP_DATETIME"] = df["FL_DATE"] * 10000 + df["DEP_TIME"]
    df["DEP_DATETIME"] = df["DEP_DATETIME"].apply(lambda x: pd.to_datetime(str(int(x))))

    # Select relevant columns.
    df = df[["DEP_DATETIME", "DEP_DELAY"]].sort_values(["DEP_DATETIME"])
    print("Completed conversion. Resulting DataFrame:\n")
    print(df)
    
    out_file = in_file[:-4] + "-cleaned.csv"
    df.to_csv(out_file, sep=",")