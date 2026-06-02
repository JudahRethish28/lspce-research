"""
Tenant Attribution Registry

Loads the PII annotation CSV (which now includes tenant_id)
and provides runtime lookup: given a PII entity text value,
which tenant does it belong to?

This is what transforms the annotation CSV from an offline
evaluation artifact into an operational runtime component.
"""
import pandas as pd
from functools import lru_cache

class TenantRegistry:

    def __init__(self, annotations_path: str):
        self.df = pd.read_csv(annotations_path)
        # Build a lookup dict: entity_text → tenant_id
        # For entities appearing in multiple tenants
        # (e.g. shared IP), record all owning tenants
        self._registry = {}
        for _, row in self.df.iterrows():
            text   = str(row["entity_text"]).strip()
            tenant = str(row["tenant_id"]).strip()
            if text not in self._registry:
                self._registry[text] = set()
            self._registry[text].add(tenant)

        print(f"[TenantRegistry] Loaded {len(self._registry)} "
              f"unique PII entity values from "
              f"{len(self.df)} annotations.")

    def get_owning_tenants(self, entity_text: str) -> set:
        """
        Returns the set of tenants that own this entity value.
        Returns empty set if entity is not in the registry
        (i.e. it was not in the ground truth annotations).
        """
        return self._registry.get(entity_text.strip(), set())

    def is_cross_tenant(
        self, entity_text: str, warrant_tenant: str
    ) -> bool:
        """
        Returns True if this entity belongs to a tenant
        other than the warrant tenant.
        """
        owners = self.get_owning_tenants(entity_text)
        if not owners:
            return False  # Unknown entity — do not flag
        return (owners and warrant_tenant not in owners)

    def get_entity_count_by_tenant(self) -> dict:
        """Returns annotation counts per tenant — for reporting."""
        return self.df["tenant_id"].value_counts().to_dict()