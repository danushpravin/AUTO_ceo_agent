# test_demand_profile.py
from ui.create_company import generate_demand_profile_llm

result = generate_demand_profile_llm(
    "D2C skincare brand selling serums and creams via paid social in India",
    ["Vitamin C Serum", "Hydra Cream", "Eye Repair Serum"]
)

import json
print(json.dumps(result, indent=2))