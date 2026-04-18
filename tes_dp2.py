# test_dp2.py
from openai import OpenAI
import json

client = OpenAI()

DEMAND_PROFILE_SYSTEM = """
You are a business simulation expert. Given a company description and product list,
generate a realistic DEMAND_PROFILE for each product.
Return ONLY valid JSON — no explanation, no markdown, no code fences.
The JSON must follow this exact structure:
{
  "Product Name": {
    "seasonality": [12 floats, one per month Jan-Dec],
    "trend": {"type": "growth", "start": 0.8, "peak_month": 6, "end": 1.0},
    "events": [{"name": "Diwali", "date": "10-20", "duration_days": 7, "multiplier": 1.6}]
  }
}
"""

try:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": DEMAND_PROFILE_SYSTEM},
            {"role": "user", "content": "Company: D2C skincare brand in India. Products: Vitamin C Serum, Hydra Cream"},
        ],
        max_tokens=2000,
        temperature=0.4,
    )
    raw = response.choices[0].message.content.strip()
    print("RAW RESPONSE:")
    print(raw)
    print("\nPARSED:")
    print(json.loads(raw))
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")