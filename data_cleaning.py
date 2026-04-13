import pandas as pd
import glob

path = 'data/matches/*.json'
files = glob.glob(path)

li = []

for file in files:
    df = pd.read_json(file)
    df['season_year'] = file.split('.')[0]
    li.append(df)
historical_df = pd.concat(li, axis=0, ignore_index=True)
df_flat = pd.json_normalize(historical_df['epa'])
historical_df = pd.concat([historical_df.drop('epa', axis=1), df_flat], axis=1)
