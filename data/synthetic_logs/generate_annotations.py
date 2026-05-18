import os
import re
import csv

# =========================================================
# CONFIGURATION
# =========================================================

LOGS_FOLDER = "data/synthetic_logs"
OUTPUT_CSV = "data/ground_truth/pii_annotations.csv"

# =========================================================
# REGULATION MAPPING
# =========================================================

REGULATION_MAP = {
    "PERSON": "GDPR_Art5_1a, DPDPA_S8",
    "IP_ADDRESS": "GDPR_Art5_1b, DPDPA_S8",
    "AWS_ARN": "GDPR_Art5_1b, DPDPA_S8",
    "AWS_ACCOUNT_ID": "GDPR_Art5_1b, DPDPA_S8"
}

# =========================================================
# REGEX PATTERNS
# =========================================================

PATTERNS = {
    "PERSON": r'"userName"\s*:\s*"([^"]+)"',
    
    "IP_ADDRESS": r'"sourceIPAddress"\s*:\s*"(\d{1,3}(?:\.\d{1,3}){3})"',
    
    "AWS_ARN": r'(arn:aws:[^"\s,]+)',
    
    "AWS_ACCOUNT_ID": r'"(?:accountId|recipientAccountId)"\s*:\s*"(\d{12})"'
}

# =========================================================
# CREATE OUTPUT DIRECTORY IF NOT EXISTS
# =========================================================

os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# =========================================================
# WRITE CSV HEADER
# =========================================================

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    
    writer = csv.writer(csvfile)
    
    writer.writerow([
        "file_name",
        "entity_text",
        "entity_type",
        "start_char",
        "end_char",
        "regulation"
    ])

    # =====================================================
    # PROCESS EACH LOG FILE
    # =====================================================

    for filename in os.listdir(LOGS_FOLDER):

        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(LOGS_FOLDER, filename)

        print(f"\nProcessing: {filename}")

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # =================================================
        # FIND ENTITIES
        # =================================================

        for entity_type, pattern in PATTERNS.items():

            matches = re.finditer(pattern, text)

            for match in matches:

                # PERSON / IP / ACCOUNT_ID use capture group
                if entity_type in ["PERSON", "IP_ADDRESS", "AWS_ACCOUNT_ID"]:
                    entity_text = match.group(1)

                    # Find exact span of captured text
                    start_char = match.start(1)
                    end_char = match.end(1)

                # ARN uses full match
                else:
                    entity_text = match.group(0)

                    start_char = match.start(0)
                    end_char = match.end(0)

                regulation = REGULATION_MAP[entity_type]

                # =========================================
                # WRITE ROW
                # =========================================

                writer.writerow([
                    filename,
                    entity_text,
                    entity_type,
                    start_char,
                    end_char,
                    regulation
                ])

                print(
                    f"  {entity_type}: {entity_text} "
                    f"({start_char}-{end_char})"
                )

print("\n===================================")
print("Annotation CSV generated successfully!")
print(f"Saved to: {OUTPUT_CSV}")
print("===================================")