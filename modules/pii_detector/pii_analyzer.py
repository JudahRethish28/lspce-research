import json, os
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from modules.pii_detector.custom_recognizers import (build_aws_arn_recognizer,
                                 build_aws_account_id_recognizer)

REGULATION_MAP = {
    "PERSON":          {"gdpr": "Art 5(1)(a)", "dpdpa": "S8"},
    "IP_ADDRESS":      {"gdpr": "Art 5(1)(b)", "dpdpa": "S8"},
    "AWS_ARN":         {"gdpr": "Art 5(1)(b)", "dpdpa": "S8"},
    "AWS_ACCOUNT_ID":  {"gdpr": "Art 5(1)(b)", "dpdpa": "S8"},
}

TARGET_ENTITIES = ["PERSON", "IP_ADDRESS",
                   "AWS_ARN", "AWS_ACCOUNT_ID"]

def build_analyzer():
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()
    registry.add_recognizer(build_aws_arn_recognizer())
    registry.add_recognizer(build_aws_account_id_recognizer())
    return AnalyzerEngine(registry=registry)

def analyze_file(filepath: str, analyzer) -> list:
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    
    results = analyzer.analyze(
        text=text,
        entities=TARGET_ENTITIES,
        language="en"
    )
   
    findings = []
    for r in results:
        entity_text = text[r.start:r.end]
        reg = REGULATION_MAP.get(r.entity_type, {})
        findings.append({
            "file": os.path.basename(filepath),
            "entity_type": r.entity_type,
            "entity_text": entity_text,
            "start": r.start,
            "end": r.end,
            "score": round(r.score, 3),
            "gdpr_clause": reg.get("gdpr", "N/A"),
            "dpdpa_clause": reg.get("dpdpa", "N/A"),
        })
    return findings