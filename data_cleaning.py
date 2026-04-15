import pandas as pd
import glob
import os
from sklearn.preprocessing import StandardScaler
from typing import cast
scaler = StandardScaler()
path = 'data/team_matches/*.json'
files = glob.glob(path)

li = []
for file in files:
    # 1. Ignore lingering temp files
    if "temp" in file:
        print(f"Skipping temp file: {file}")
        continue

    print(f"Reading: {file}")

    # 2. Catch corrupted JSON files gracefully
    try:
        # Changed "winner" to ["winner"] to avoid future Pandas deprecation warnings
        df = pd.read_json(file).dropna(subset=["winner"])
        df['season_year'] = os.path.basename(file).split('.')[0]
        li.append(df)
    except ValueError as e:
        print(f"❌ ERROR reading {file}: {e} (File is likely corrupted)")
        continue

if not li:
    raise ValueError("No valid data files found to process!")

historical_df = pd.concat(li, axis=0, ignore_index=True)

epa_expanded = pd.json_normalize(historical_df['epa'])

# 2. If 'breakdown' exists inside that new dataframe, expand it too
if 'breakdown' in epa_expanded.columns:
    # Normalize the breakdown column
    breakdown_expanded = pd.json_normalize(epa_expanded['breakdown']).add_prefix('breakdown_')

    # Drop the original breakdown and join the new columns
    epa_final = pd.concat([
        epa_expanded.drop(columns=['breakdown']).add_prefix('epa_'),
        breakdown_expanded.add_prefix('epa_')
    ], axis=1)
else:
    epa_final = epa_expanded.add_prefix('epa_')

# 3. Join back to original DF using the index to prevent shifting
historical_df = historical_df.drop(columns=['epa']).join(epa_final).fillna(0)

# Check the results
# print(historical_df.columns)

historical_df['universal_auto'] = historical_df['epa_breakdown.auto_points']
historical_df['universal_teleop'] = historical_df['epa_breakdown.teleop_points']
historical_df['universal_endgame'] = historical_df['epa_breakdown.endgame_points']

historical_df['universal_pieces'] = (
    historical_df['epa_breakdown.total_fuel'].fillna(0) +        # 2026
    historical_df['epa_breakdown.total_game_pieces'].fillna(0) + # 2025
    historical_df['epa_breakdown.total_notes'].fillna(0) +       # 2024
    historical_df['epa_breakdown.total_pieces'].fillna(0) +      # 2023
    historical_df['epa_breakdown.cargo'].fillna(0)               # 2022
)

historical_df['universal_rp_contribution'] = (
    historical_df['epa_breakdown.rp_1'].fillna(0) +
    historical_df['epa_breakdown.rp_2'].fillna(0) +
    historical_df['epa_breakdown.rp_3'].fillna(0)
)

historical_df['universal_support_value'] = (
    historical_df['epa_breakdown.transition_fuel'].fillna(0) + # 2026
    historical_df['epa_breakdown.processor_algae_points'].fillna(0) + # 2025
    historical_df['epa_breakdown.amp_points'].fillna(0) # 2024 (Support role)
)


historical_df['scaled_pieces'] = historical_df.groupby('year')['universal_pieces'].transform(
    lambda x: scaler.fit_transform(x.values.reshape(-1, 1)).flatten()
)


