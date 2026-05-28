import json, os, time
from modules.scope_validator.scope_validator import validate_scope
import time

PAIRS_DIR = "data/ground_truth/warrant_plan_pairs"
results = []

for i in range(1, 31):
    num = f"{i:02d}"
    warrant = json.load(open(f"{PAIRS_DIR}/warrant_{num}.json"))
    plan    = json.load(open(f"{PAIRS_DIR}/plan_{num}.json"))
    label   = json.load(open(f"{PAIRS_DIR}/label_{num}.json"))
    
    start = time.time()
    result = validate_scope(warrant, plan)
    elapsed = time.time() - start
    
    results.append({
    "pair_id": num,
    "expected": label["verdict"],
    "predicted": result["verdict"],
    "correct": result["verdict"] == label["verdict"],
    "issues_predicted": result.get("issues", []),
    "issues_expected": label.get("issues", []),
    "runtime_seconds": round(elapsed, 2)
    })
    with open("evaluation/scope_validation_raw_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Pair {num}: {result['verdict']} "
          f"({'✓' if result['verdict']==label['verdict'] else '✗'})")
    time.sleep(10)

# Save results

print(f"\nDone. Saved {len(results)} results.")