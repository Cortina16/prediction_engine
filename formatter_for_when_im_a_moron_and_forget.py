import json

def pretty(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

pretty('historical_data.json')