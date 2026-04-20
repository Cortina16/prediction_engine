from scipy.stats import skewnorm
import numpy as np
import polars as pl

def simulate_full_profile(teams, profiles, iterations=1000):
    alliance_total_scores = np.zeros(iterations)

    for team in teams:
        stats = profiles.filter(pl.col("team") == team)

        # 1. Base + Value Add + Momentum
        # We adjust the mean based on how much they've improved (momentum)
        adj_mu = stats["avg_real_points"][0] + stats["momentum"][0]

        # 2. Consistency
        sigma = stats["consistency_std"][0]

        # 3. Upside Skew
        # 'a' is the skewness parameter in skewnorm
        skew_param = stats["upside_skew"][0]

        # Generate random scores using the skewed distribution
        #
        team_sim_scores = skewnorm.rvs(a=skew_param, loc=adj_mu, scale=sigma, size=iterations)

        alliance_total_scores += team_sim_scores

    return alliance_total_scores

# Then compare Red vs Blue
# red_sim = simulate_full_profile(red_teams, profiles)
# blue_sim = simulate_full_profile(blue_teams, profiles)
# win_prob = (red_sim > blue_sim).mean()

def sim(match_keys, test_matches,train_profiles):
    results = []

    for m_key in match_keys:
        match_data = test_matches.filter(pl.col("match") == m_key)

        red_teams = match_data.filter(pl.col("alliance") == "red")["team"].to_list()
        blue_teams = match_data.filter(pl.col("alliance") == "blue")["team"].to_list()

        if len(red_teams) != 3 or len(blue_teams) != 3:
            continue

        red_sim = simulate_full_profile(red_teams, train_profiles)
        blue_sim = simulate_full_profile(blue_teams, train_profiles)

        red_win_prob = (red_sim > blue_sim).mean()

        actual_red_win = match_data.filter(pl.col("alliance") == "red")["won"].cast(pl.Boolean).any()
        # print(actual_red_win)
        results.append({
            "match": m_key,
            "red_prob": red_win_prob,
            "predicted_winner": "red" if red_win_prob > 0.5 else "blue",
            "actual_winner": "red" if actual_red_win else "blue"
        })

    sim_df = pl.DataFrame(results)
    accuracy = (sim_df["predicted_winner"] == sim_df["actual_winner"]).mean()

    print(f"Simulation done")
    print(f"Total Matches Simulated: {len(sim_df)}")
    print(f"Prediction Accuracy: {accuracy * 100:.2f}%")