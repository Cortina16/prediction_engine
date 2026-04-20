import ijson
import os

def validate_json_syntax(folder):
    for file in os.listdir(folder):
        if file.endswith(".json") and "_temp" not in file:
            path = os.path.join(folder, file)
            try:
                with open(path, 'rb') as f:
                    for _ in ijson.items(f, 'item'):
                        pass
                print(f"✅ {file} is valid.")
            except Exception as e:
                print(f"❌ {file} is CORRUPT: {e}")

validate_json_syntax('data/matches')

