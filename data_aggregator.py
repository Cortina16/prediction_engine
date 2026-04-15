import json
import os
import shutil

import statbotics

sb = statbotics.Statbotics()

def team_data(start_year = 2022, end_year = 2026):
    all_years_data = []
    for year in range(start_year, end_year+1):
        if os.path.exists(f'data/teams/{year}.json'):
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
        with open(f'data/teams/{year}.json', 'w') as outfile:
            json.dump(all_years_data, outfile, indent=4)
            all_years_data = []

def game_data(start_year = 2022, end_year = 2026):
    all_years_data = []
    for year in range(start_year, end_year+1):
        if os.path.exists(f'data/games/{year}.json'):
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
        with open(f'data/games/{year}.json', 'w') as outfile:
            json.dump(all_years_data, outfile, indent=4)
            all_years_data = []

def team_match_data(start_year = 2022, end_year = 2026):
    all_years_data = []
    for year in range(start_year, end_year+1):
        if os.path.exists(f'data/team_matches/{year}.json'):
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
        with open(f'data/team_matches/{year}.json', 'w') as outfile:
            json.dump(all_years_data, outfile, indent=4)
            all_years_data = []

def match_data(start_year = 2022, end_year = 2026):
    all_years_data = []
    for year in range(start_year, end_year+1):
        if os.path.exists(f'data/matches/{year}.json'):
            continue

        for offset in range (0, 3000):
            try:
                year_data = sb.get_matches(year=year,limit=1000, offset=offset*1000)
                if not year_data or len(year_data) == 0:
                    break
                all_years_data.extend(year_data)

            except Exception as e:
                print(e)
                break
        with open(f'data/matches/{year}.json', 'w') as outfile:
            json.dump(all_years_data, outfile, indent=4)
            all_years_data = []

def move_data():
    for year in range(2022, 2027):
        match_path = f'data/matches/{year}.json'
        team_match_path = f'data/team_matches/{year}.json'

        # Safety check: skip if files are missing
        if not os.path.exists(match_path) or not os.path.exists(team_match_path):
            print(f"Skipping {year}: Missing one of the required files.")
            continue

        with open(match_path, 'r') as f:
            all_years_data = json.load(f)
        with open(team_match_path, 'r') as f:
            team_list_data = json.load(f)
        match_map = {
            m['key']: {
                'winner' : m["result"].get("winner"),
                'red_score' : m["result"].get("red_score"),
                'blue_score' : m["result"].get("blue_score"),
            } for m in all_years_data if m.get("result")
        }

        for item in team_list_data:
            match_info = match_map.get(item['match'])
            if match_info:
                item.update(match_info)
                item['won'] = 1 if item['alliance'] == item['winner'] else (2 if item['winner'] == 'tie' else 0)
                if item['alliance'] == 'red':
                    item['alliance_score'] = item['red_score']
                    item['opponent_score'] = item['blue_score']
                else:
                    item['alliance_score'] = item['blue_score']
                    item['opponent_score'] = item['red_score']
        temp_path = f'data/team_matches/{year}_temp.json'
        with open(temp_path, 'w') as outfile:
            json.dump(team_list_data, outfile, indent=4)

        os.replace(temp_path, team_match_path)
        print(f"Successfully processed {year}")


team_match_data()
match_data()
move_data()