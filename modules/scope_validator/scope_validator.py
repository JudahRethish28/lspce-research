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

def reassess_scope_post_collection(
    pre_verdict: str,
    cross_tenant_violations: list,
    pii_findings: list
) -> dict:
    """
    After evidence is collected and PII is detected,
    reassess the scope verdict incorporating actual findings.
    This is the function that makes PII operationally relevant.
    """
    has_cross_tenant = len(cross_tenant_violations) > 0
    has_pii          = len(pii_findings) > 0

    if has_cross_tenant:
        final_verdict    = "PRIVACY_VIOLATION"
        recommendation   = "BLOCK"
        explanation      = (
            f"Collection contained {len(cross_tenant_violations)} "
            f"PII entities belonging to tenants other than the "
            f"warrant tenant. Evidence package must be blocked."
        )
    elif pre_verdict == "OVER_COLLECTION":
        # Should not reach here — OVER_COLLECTION halts before
        # collection. But handle defensively.
        final_verdict    = "OVER_COLLECTION"
        recommendation   = "BLOCK"
        explanation      = "Pre-collection scope check failed."
    elif has_pii:
        final_verdict    = "APPROVED_PII_PRESENT"
        recommendation   = "REDACT"
        explanation      = (
            f"Collection is within legal scope but contains "
            f"{len(pii_findings)} PII entities. Redact before handoff."
        )
    else:
        final_verdict    = "APPROVED_CLEAN"
        recommendation   = "RELEASE"
        explanation      = (
            "Collection is within legal scope and contains no "
            "detectable PII. Evidence package cleared for handoff."
        )

    return {
        "pre_collection_verdict":  pre_verdict,
        "post_collection_verdict": final_verdict,
        "recommendation":          recommendation,
        "explanation":             explanation,
        "cross_tenant_violations": len(cross_tenant_violations),
        "total_pii_entities":      len(pii_findings)
    }