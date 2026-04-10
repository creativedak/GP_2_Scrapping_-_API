import glob
import pandas as pd

files = glob.glob("*.csv")

dfs = []
for f in files:
    df = pd.read_csv(f)
    dfs.append(df)

result = pd.concat(dfs, ignore_index=True)
result.to_csv("kvartiri-final.csv", index=False, encoding="utf-8-sig")
files = glob.glob("*.log")

with open("logs-final.log", "w", encoding="utf-8") as outfile:
    for f in files:
        with open(f, "r", encoding="utf-8") as infile:
            outfile.write(infile.read())
            outfile.write("\n")
