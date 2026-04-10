import pandas as pd

df1 = pd.read_csv('links_30-60.csv')
df2 = pd.read_csv('links_60+.csv')
df3 = pd.read_csv('links_21-30.csv')
df4 = pd.read_csv('links_1-10.csv')
df5 = pd.read_csv('links_11-20.csv')
combined_df = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)

combined_df.to_csv('urls.csv')
