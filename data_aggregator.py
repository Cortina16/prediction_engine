import json
import os

import statbotics

sb = statbotics.Statbotics()

def team_data(start_year = 2022, end_year = 2025):
    all_years_data = []
    for year in range(start_year, end_year+1):
        if os.path.exists(f'data/team/{year}.json'):
            continue

        for offset in range (0, 3000):
            try:
                year_data = sb.get_team_years(year=year,limit=1000, offset=offset*1000)
                if not year_data or len(year_data) == 0:
                    break
                all_years_data.extend(year_data)

            except Exception as e:
                print(e)
                break
        with open(f'data/team/{year}.json', 'w') as outfile:
            json.dump(all_years_data, outfile, indent=4)
            all_years_data = []

def game_data(start_year = 2022, end_year = 2025):
    all_years_data = []
    for year in range(start_year, end_year+1):
        if os.path.exists(f'data/game/{year}.json'):
            continue

        for offset in range (0, 3000):
            try:
                year_data = sb.get_team_events(year=year,limit=1000, offset=offset*1000)
                if not year_data or len(year_data) == 0:
                    break
                all_years_data.extend(year_data)

            except Exception as e:
                print(e)
                break
        with open(f'data/game/{year}.json', 'w') as outfile:
            json.dump(all_years_data, outfile, indent=4)
            all_years_data = []

def match_data(start_year = 2022, end_year = 2025):
    all_years_data = []
    for year in range(start_year, end_year+1):
        if os.path.exists(f'data/matches/{year}.json'):
            continue

        for offset in range (0, 3000):
            try:
                year_data = sb.get_team_matches(year=year,limit=1000, offset=offset*1000)
                if not year_data or len(year_data) == 0:
                    break
                all_years_data.extend(year_data)

            except Exception as e:
                print(e)
                break
        with open(f'data/matches/{year}.json', 'w') as outfile:
            json.dump(all_years_data, outfile, indent=4)
            all_years_data = []



game_data(start_year = 2022, end_year = 2025)
team_data(start_year = 2022, end_year = 2025)
