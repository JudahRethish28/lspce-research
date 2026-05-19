import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.scope_validator_v0 import validate_scope
import json

warrant = json.load(open(
    "data/ground_truth/warrant_plan_pairs/warrant_21.json"
))

plan = json.load(open(
    "data/ground_truth/warrant_plan_pairs/plan_21.json"
))

label = json.load(open(
    "data/ground_truth/warrant_plan_pairs/label_21.json"
))

result = validate_scope(warrant, plan)

print("Verdict:", result["verdict"])
print("Expected:", label["verdict"])
print("Match:", result["verdict"] == label["verdict"])