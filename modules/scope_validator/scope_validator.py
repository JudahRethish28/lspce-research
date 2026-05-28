import google.generativeai as genai
import os, json, re
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

FEW_SHOT = """
EXAMPLE 1 — APPROVED:
Warrant: tenant-a, May 1-3, cloudtrail_management only
Plan: tenant-a, May 1-3, cloudtrail_management only
Output: {"verdict":"APPROVED","issues":[],"confidence":0.98}

EXAMPLE 2 — OVER_COLLECTION:
Warrant: tenant-a, May 1-3, cloudtrail_management only
Plan: tenant-b, May 1-3, cloudtrail_management only
Output: {"verdict":"OVER_COLLECTION",
"issues":["plan targets tenant-b, warrant specifies tenant-a"],
"confidence":0.97}

EXAMPLE 3 — UNDER_COLLECTION:
Warrant: tenant-a, May 1-7, cloudtrail + s3_data_events
Plan: tenant-a, May 1-7, cloudtrail_management only
Output: {"verdict":"UNDER_COLLECTION",
"issues":["s3_data_events authorised but not in plan"],
"confidence":0.95}
"""

PROMPT_TEMPLATE = """
You are a forensic evidence scope validator...

{few_shot}

WARRANT:
{warrant}

COLLECTION PLAN:
{plan}

Respond with ONLY a JSON object.
"""

def validate_scope(warrant: dict, plan: dict) -> dict:

    prompt = PROMPT_TEMPLATE.format(
        few_shot=FEW_SHOT,
        warrant=json.dumps(warrant, indent=2),
        plan=json.dumps(plan, indent=2)
    )

    response = model.generate_content(prompt)

    text = response.text.strip()

    text = re.sub(r'^```(?:json)?\n?', '', text)
    text = re.sub(r'\n?```$', '', text)

    return json.loads(text.strip())