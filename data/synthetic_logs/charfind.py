file_path = "data/synthetic_logs/tenant-a_log_00.json"

with open(file_path, "r") as f:
    text = f.read()

entity = "alice.chen"

start = text.find(entity)
end = start + len(entity)

print(start)
print(end)