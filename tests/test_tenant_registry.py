from modules.tenant_registry.tenant_registry import TenantRegistry

registry = TenantRegistry("data/ground_truth/pii_annotations.csv")

# Test 1: Look up a known tenant-a entity
# Find any entity_text value from your CSV for tenant-a
# e.g. "alice.chen"
owners = registry.get_owning_tenants("alice.chen")
print(f"alice.chen belongs to: {owners}")  # Should show {'tenant-a'}

# Test 2: Cross-tenant check
is_cross = registry.is_cross_tenant("alice.chen", "tenant-b")
print(f"alice.chen is cross-tenant for tenant-b: {is_cross}")
# Should print True

# Test 3: Unknown entity
owners = registry.get_owning_tenants("random_string_xyz")
print(f"Unknown entity owners: {owners}")  # Should show set()