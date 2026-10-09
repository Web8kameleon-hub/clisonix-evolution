import yaml

FILE_PATH = "docker-compose.unified.yml"

with open(FILE_PATH, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

services = data.get("services", {})

updated_labs = 0
for name, svc in services.items():
    if not isinstance(svc, dict):
        continue
    if name.endswith("-lab"):
        env = svc.get("environment")
        if not isinstance(env, dict):
            env = {}
            svc["environment"] = env
        changed = False
        if env.get("LAB_PORT") != "8100":
            env["LAB_PORT"] = "8100"
            changed = True
        if "PORT" in env:
            del env["PORT"]
            changed = True
        if changed:
            updated_labs += 1

loki = services.get("loki")
if isinstance(loki, dict):
    loki["profiles"] = ["monitoring"]

with open(FILE_PATH, "w", encoding="utf-8") as f:
    yaml.dump(data, f, sort_keys=False, allow_unicode=True)

print(f"Updated labs LAB_PORT=8100: {updated_labs}")
print("Loki set to optional profile: monitoring")
