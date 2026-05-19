import google.generativeai as genai
import os, json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def validate_scope(warrant: dict, plan: dict) -> dict:
    prompt = f"""
You are a forensic evidence scope validator.
Your task: compare a legal warrant with a proposed 
evidence collection plan. Determine if the plan 
is APPROVED, OVER_COLLECTION, or UNDER_COLLECTION.

DEFINITIONS:
- APPROVED: plan collects exactly what warrant allows
- OVER_COLLECTION: plan collects more than warrant allows
  (wrong tenant, wider time window, extra evidence types)
- UNDER_COLLECTION: plan misses evidence the warrant allows
  (narrower time window, fewer evidence types than authorised)

Return ONLY a JSON object with these exact keys:
{{
  "verdict": "APPROVED" or "OVER_COLLECTION" or "UNDER_COLLECTION",
  "issues": ["list of specific problems found, empty if APPROVED"],
  "approved_resources": ["list of resource types that are valid"]
}}

WARRANT:
{json.dumps(warrant, indent=2)}

COLLECTION PLAN:
{json.dumps(plan, indent=2)}
"""
    response = model.generate_content(prompt)
    # Strip markdown code fences if model adds them
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())