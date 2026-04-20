import numpy as np
import polars as pl
import glob
import os
import sim_data
path = 'data/team_matches/*.json'
files = [f for f in glob.glob(path) if "temp" not in f]
files = glob.glob('data/team_matches/2026.json')

def load_and_flatten(file):
    year = os.path.basename(file).split('.')[0]
    df = pl.read_json(file)

    if "epa" in df.columns:
        df = df.with_columns(
            pl.col("epa").struct.rename_fields([
                f"epa_{fld}" for fld in df["epa"].struct.fields
            ])
        ).unnest("epa")

        if "epa_breakdown" in df.columns:
            df = df.with_columns(
                pl.col("epa_breakdown").struct.rename_fields([
                    f"brk_{fld}" for fld in df["epa_breakdown"].struct.fields
                ])
            ).unnest("epa_breakdown")

    identifiers = ["winner", "team", "match", "alliance", "season_year"]

    return df.with_columns([
        pl.lit(year).alias("season_year"),
        pl.all().exclude(identifiers).cast(pl.Float64, strict=False)
    ])


print("Flattening and merging all years...")
all_dfs = [load_and_flatten(f) for f in files]

lf = pl.concat(all_dfs, how="diagonal").lazy()

cols = lf.collect_schema().names()
piece_keys = ["brk_total_fuel", "brk_total_game_pieces", "brk_cargo", "brk_total_notes", "brk_total_pieces"]
existing_pieces = [pl.col(k) for k in piece_keys if k in cols]

lf = (
    lf.filter(pl.col("winner").is_not_null())
    .with_columns([
        pl.col("epa_total_points").sum().over(["match", "alliance"]).alias("alliance_total_epa"),

        pl.sum_horizontal(existing_pieces).fill_null(0).alias("universal_pieces")
    ])
    .with_columns([
        (pl.col("alliance_total_epa") - pl.col("epa_total_points")).alias("partner_epa_sum")
    ])
    .with_columns([
        (pl.col("alliance_score").cast(pl.Float64, strict=False) - pl.col("partner_epa_sum")).alias("real_contribution")
    ])
)

lf = lf.with_columns([
    (pl.col("epa_total_points") - pl.col("epa_total_points").shift(1).over(["season_year", "team"]))
    .fill_null(0)
    .alias("epa_velocity")
])

event_lf = lf.with_columns(
    match_num = pl.col("match").str.extract(r"qm(\d+)$").cast(pl.Int32)
).sort("match_num")
total_matches = event_lf.select(pl.col("match_num").max()).collect().item()
split_point = total_matches // 2

train_profiles = (
    event_lf.filter(pl.col("match_num") <= split_point)
    .group_by("team")
    .agg([
        pl.col("real_contribution").mean().alias("avg_real_points"),
        pl.col("real_contribution").quantile(0.90).alias("peak_real_points"),
        pl.col("real_contribution").std().alias("consistency_std"),
        pl.col("real_contribution").skew().alias("upside_skew"),
        pl.col("epa_velocity").mean().alias("momentum"),
        # pl.col("avg_epa").first(),
        pl.col("epa_total_points").mean().alias("avg_epa"),
        pl.col("universal_pieces").mean().alias("avg_cycle_volume"),
        pl.col("won").cast(pl.Float64, strict=False).mean().alias("win_rate")
    ])
    .with_columns([
        (pl.col("avg_real_points") - pl.col("avg_epa")).alias("value_add"),
        (pl.col("peak_real_points") - pl.col("avg_real_points")).alias("upset_potential")
    ])
).collect()
train_profiles.with_columns([
    pl.col("consistency_std").fill_null(5.0), # Default to a conservative 5-point spread
    pl.col("upside_skew").fill_null(0.0)      # Assume no skew if we don't know yet
])

# 1. Get the "Future" schedule (matches after the split)
# We need to collect it to iterate through it easily
test_matches = event_lf.filter(pl.col("match_num") > split_point).collect()

# We need to group by match to get the Red and Blue alliances
match_keys = test_matches["match"].unique().to_list()

sim_data.sim(match_keys, test_matches, train_profiles,)


team_profiles = (
    lf.group_by(["season_year", "team"])
    .agg([
        pl.col("real_contribution").mean().alias("avg_real_points"),
        pl.col("real_contribution").quantile(0.90).alias("peak_real_points"),
        pl.col("real_contribution").std().alias("consistency_std"),
        pl.col("real_contribution").skew().alias("upside_skew"),
        pl.col("epa_velocity").mean().alias("momentum"),
        # pl.col("avg_epa").first(),
        pl.col("epa_total_points").mean().alias("avg_epa"),
        pl.col("universal_pieces").mean().alias("avg_cycle_volume"),
        pl.col("won").cast(pl.Float64, strict=False).mean().alias("win_rate")
    ])
    .with_columns([
        (pl.col("avg_real_points") - pl.col("avg_epa")).alias("value_add"),
        (pl.col("peak_real_points") - pl.col("avg_real_points")).alias("upset_potential")
    ])
)
data = lf.collect()
final_df = team_profiles.collect()
final_df_pd = final_df.to_pandas()
print(final_df.sort("value_add", descending=True).head(10))