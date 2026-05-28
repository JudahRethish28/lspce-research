import json
from modules.scope_validator.scope_validator import validate_scope

for pair_num in ["01", "11", "21"]:
    warrant = json.load(open(
        f"data/ground_truth/warrant_plan_pairs/warrant_{pair_num}.json"))
    plan    = json.load(open(
        f"data/ground_truth/warrant_plan_pairs/plan_{pair_num}.json"))
    label   = json.load(open(
        f"data/ground_truth/warrant_plan_pairs/label_{pair_num}.json"))

    result  = validate_scope(warrant, plan)
    match   = result["verdict"] == label["verdict"]

    print(f"Pair {pair_num}: expected={label['verdict']}"
          f" got={result['verdict']} match={match}")