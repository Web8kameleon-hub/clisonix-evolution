#!/usr/bin/env python3
"""Build selected services against their installed dependencies; preserve runtime config.

Run prepare before apply. Runtime snapshots contain secrets and stay mode 0600
on the host. The existing checkout is never reset, stashed, or overwritten.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

SERVICES = {
    "web": "clisonix-web",
    "api": "clisonix-api",
    "ocean-core": "clisonix-ocean-core",
    "ocean-mission-service": "clisonix-ocean-mission",
    "translation-node": "clisonix-translation-node",
    "ocean-core-multimodal": "clisonix-ocean-core-multimodal",
}


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def inspect(name):
    return json.loads(subprocess.check_output(["docker", "inspect", name]))[0]


def private_json(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as output:
        json.dump(data, output)
    os.chmod(path, 0o600)


def source_files(service, changed):
    if service == "api":
        return [f for f in changed if f.startswith("apps/api/") and f.endswith(".py")]
    if service == "ocean-mission-service":
        return ["ocean-core/ocean_mission_service.py"]
    if service == "translation-node":
        return ["ocean-core/translation_node.py"]
    if service == "ocean-core-multimodal":
        return ["ocean-core/ocean_multimodal.py"]
    return [f for f in changed if f.startswith("ocean-core/")
            and not f.startswith("ocean-core/tests/")
            and Path(f).suffix in {".py", ".yaml"}]


def runtime_service(old, image, networks, volumes):
    config, host = old["Config"], old["HostConfig"]
    service = {
        "image": image, "container_name": old["Name"].lstrip("/"),
        "environment": config["Env"],
        "restart": host["RestartPolicy"]["Name"] or "no",
        "networks": {}, "volumes": [], "ports": [],
        "labels": {k: v for k, v in (config.get("Labels") or {}).items()
                   if not k.startswith("com.docker.compose.")},
    }
    retries = host["RestartPolicy"].get("MaximumRetryCount")
    if retries:
        service["restart"] += ":" + str(retries)
    if host.get("LogConfig", {}).get("Type"):
        service["logging"] = {"driver": host["LogConfig"]["Type"],
                              "options": host["LogConfig"].get("Config") or {}}
    if host.get("Ulimits"):
        service["ulimits"] = {u["Name"]: {"soft": u["Soft"], "hard": u["Hard"]}
                             for u in host["Ulimits"]}
    if host.get("Devices"):
        service["devices"] = [d["PathOnHost"] + ":" + d["PathInContainer"] + ":" + d["CgroupPermissions"]
                              for d in host["Devices"]]
    if host.get("Tmpfs"):
        service["tmpfs"] = [path + ":" + options for path, options in host["Tmpfs"].items()]
    if config.get("Cmd") is not None:
        service["command"] = config["Cmd"]
    if config.get("Entrypoint") is not None:
        service["entrypoint"] = config["Entrypoint"]
    for original, target in [("User", "user"), ("WorkingDir", "working_dir")]:
        if config.get(original):
            service[target] = config[original]
    for name, network in old["NetworkSettings"]["Networks"].items():
        key = "net_" + str(len(networks)) if name not in networks else networks[name]
        networks[name] = key
        aliases = [x for x in network.get("Aliases") or []
                   if x != old["Id"][:12] and x != old["Id"]]
        service["networks"][key] = {"aliases": aliases}
    for mount in old["Mounts"]:
        if mount["Type"] not in {"bind", "volume"}:
            raise ValueError("Unsupported mount type: " + mount["Type"])
        item = {"type": mount["Type"], "source": mount["Source"],
                "target": mount["Destination"], "read_only": not mount["RW"]}
        if mount["Type"] == "volume":
            name = mount["Name"]
            key = volumes.setdefault(name, "vol_" + str(len(volumes)))
            item["source"] = key
        else:
            item["bind"] = {"create_host_path": False}
            if mount.get("Propagation"):
                item["bind"]["propagation"] = mount["Propagation"]
        service["volumes"].append(item)
    for port, bindings in (host.get("PortBindings") or {}).items():
        target, protocol = port.split("/")
        for binding in bindings or []:
            service["ports"].append({"target": int(target),
                                     "published": binding["HostPort"],
                                     "host_ip": binding["HostIp"] or "0.0.0.0",
                                     "protocol": protocol})
    if config.get("Healthcheck"):
        check = config["Healthcheck"]
        service["healthcheck"] = {"test": check["Test"]}
        for original, target in [("Interval", "interval"), ("Timeout", "timeout"),
                                 ("StartPeriod", "start_period")]:
            if check.get(original):
                service["healthcheck"][target] = str(check[original]) + "ns"
        if check.get("Retries"):
            service["healthcheck"]["retries"] = check["Retries"]
    for original, target in [("Memory", "mem_limit"), ("MemorySwap", "memswap_limit"),
                             ("PidsLimit", "pids_limit"), ("ShmSize", "shm_size"),
                             ("CapAdd", "cap_add"), ("CapDrop", "cap_drop"),
                             ("SecurityOpt", "security_opt"), ("ExtraHosts", "extra_hosts")]:
        if host.get(original):
            service[target] = host[original]
    if host.get("NanoCpus"):
        service["cpus"] = host["NanoCpus"] / 1e9
    if host.get("Privileged"):
        service["privileged"] = True
    if host.get("ReadonlyRootfs"):
        service["read_only"] = True
    if host.get("DeviceRequests"):
        service["deploy"] = {"resources": {"reservations": {"devices": [
            {"driver": d.get("Driver") or "nvidia",
             "capabilities": [c for group in d["Capabilities"] for c in group],
             **({"device_ids": d["DeviceIDs"]} if d.get("DeviceIDs")
                else {"count": "all" if d["Count"] == -1 else d["Count"]})}
            for d in host["DeviceRequests"]]}}}
    return service


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "apply", "rollback"])
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--services", required=True)
    args = parser.parse_args()
    selected = args.services.split(",")
    if not selected or any(s not in SERVICES for s in selected):
        parser.error("An explicit supported service list is required")
    release = args.release.resolve()
    state = release / ".runtime"
    state.mkdir(mode=0o700, exist_ok=True)
    os.chmod(state, 0o700)
    candidate, rollback = state / "candidate.json", state / "rollback.json"
    if args.mode == "prepare":
        changed = json.loads((release / "changed-files.json").read_text())
        snapshots = {s: inspect(SERVICES[s]) for s in selected}
        if any(not snapshot["State"]["Running"] for snapshot in snapshots.values()):
            raise RuntimeError("Selected containers must be running before preparation")
        private_json(state / "containers.json", snapshots)
        networks, volumes = {}, {}
        new, old = {}, {}
        for service in selected:
            snapshot = snapshots[service]
            image = "clisonix-scoped/" + service + ":" + release.name
            previous_image = "clisonix-scoped/previous-" + service + ":" + release.name
            run(["docker", "tag", snapshot["Image"], previous_image])
            if service == "web":
                command = ["docker", "build", "-f", str(release / "apps/web/Dockerfile"), "-t", image]
                env = dict(x.split("=", 1) for x in snapshot["Config"]["Env"] if "=" in x)
                for key in ["NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY", "NEXT_PUBLIC_API_BASE", "NEXT_PUBLIC_AUTH_PROVIDER"]:
                    command += ["--build-arg", key + "=" + env.get(key, "")]
                run(command + [str(release / "apps/web")])
            else:
                files = source_files(service, changed)
                if not files:
                    raise ValueError("No changed source files for " + service)
                dockerfile = state / (service + ".Dockerfile")
                dockerfile.write_text("FROM " + previous_image + "\n" + "".join(
                    "COPY " + f + " /app/" + f.split("/", 2 if service == "api" else 1)[-1] + "\n"
                    for f in files))
                run(["docker", "build", "-f", str(dockerfile), "-t", image, str(release)])
                python_paths = ["/app/" + f.split("/", 2 if service == "api" else 1)[-1]
                                for f in files if f.endswith(".py")]
                run(["docker", "run", "--rm", "--entrypoint", "python", image, "-c",
                     "import ast,sys; [ast.parse(open(p).read(),filename=p) for p in sys.argv[1:]]",
                     *python_paths])
            new[service] = runtime_service(snapshot, image, networks, volumes)
            old[service] = runtime_service(snapshot, previous_image, networks, volumes)
        external = {key: {"external": True, "name": name} for name, key in networks.items()}
        external_volumes = {key: {"external": True, "name": name} for name, key in volumes.items()}
        private_json(candidate, {"services": new, "networks": external, "volumes": external_volumes})
        private_json(rollback, {"services": old, "networks": external, "volumes": external_volumes})
        run(["docker", "compose", "-p", "clisonixcom", "-f", str(candidate), "config", "--quiet"])
        print("Prepared selected images and private runtime snapshots", flush=True)
        return
    compose = rollback if args.mode == "rollback" else candidate
    snapshots = json.loads((state / "containers.json").read_text())
    if args.mode == "apply":
        for service in selected:
            if inspect(SERVICES[service])["Id"] != snapshots[service]["Id"]:
                raise RuntimeError("Container changed since prepare: " + service)
    command = ["docker", "compose", "-p", "clisonixcom", "-f", str(compose)]
    started = []
    try:
        for service in selected:
            started.append(service)
            run(command + ["up", "-d", "--no-deps", "--force-recreate", service])
            deadline = time.monotonic() + 240
            while time.monotonic() < deadline:
                status = inspect(SERVICES[service])["State"]
                health = status.get("Health", {}).get("Status")
                if status.get("Running") and health == "healthy":
                    print(service + " healthy", flush=True)
                    break
                if not status.get("Running") or health == "unhealthy":
                    raise RuntimeError(service + " failed health")
                time.sleep(3)
            else:
                raise RuntimeError(service + " timed out")
    except Exception:
        if args.mode == "apply":
            run(["docker", "compose", "-p", "clisonixcom", "-f", str(rollback),
                 "up", "-d", "--no-deps", "--force-recreate", *started])
            print("Restored previous images for attempted services", flush=True)
        raise


if __name__ == "__main__":
    main()
