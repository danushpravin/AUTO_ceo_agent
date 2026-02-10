from pathlib import Path
import json

def load_config(company_id):
    path = Path("data/companies") / company_id / "config.json"
    with open(path, "r") as f:
        return json.load(f)

def save_config(company_id, config):
    path = Path("data/companies") / company_id / "config.json"
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
