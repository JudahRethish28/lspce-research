import json, jsonschema
from pathlib import Path

SCHEMA_DIR = Path(__file__).parent

def load_schema(name):
    with open(SCHEMA_DIR / f"{name}_schema.json") as f:
        return json.load(f)

def validate(data, schema_name):
    schema = load_schema(schema_name)
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, e.message