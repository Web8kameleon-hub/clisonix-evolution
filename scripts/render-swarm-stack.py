#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


UNSUPPORTED_SERVICE_KEYS = {
    "build",
    "container_name",
    "depends_on",
    "develop",
    "links",
    "ports",
    "profiles",
    "restart",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mapping-output", required=True, type=Path)
    parser.add_argument("--services", required=True)
    parser.add_argument("--network", default="clisonix-swarm")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    available = source.get("services", {})
    # The resolved `docker compose config --format json` payload's top-level
    # "name" is the real, authoritative Compose project name docker itself
    # uses to tag build-only services as "<project>-<service>" (verified
    # against actual `docker compose build` output, e.g. "clisonixcom-web").
    # Reading it here instead of hardcoding a project name keeps this script
    # correct even if the deploy path/project name ever changes.
    project_name = source.get("name")
    selected = [item.strip() for item in args.services.split(",") if item.strip()]
    missing = sorted(set(selected) - set(available))
    if missing:
        raise SystemExit(f"Unknown services: {', '.join(missing)}")

    rendered_services = {}
    legacy_containers = {}
    for name in selected:
        original = available[name]
        if "healthcheck" not in original:
            raise SystemExit(
                f"Service '{name}' has no real healthcheck; refusing zero-downtime deployment"
            )
        image = original.get("image")
        if not image:
            # Build-only services (no explicit `image:` in compose-hosting.yml)
            # are still deployable: `docker compose build` already tagged them
            # as "<project>-<service>" before this script runs. Compute the
            # same tag rather than requiring every service to redundantly
            # hardcode an image name that must stay in sync with the real
            # Compose project name.
            if not original.get("build") or not project_name:
                raise SystemExit(f"Service '{name}' has no deployable image")
            image = f"{project_name}-{name}"

        service = {
            key: value
            for key, value in original.items()
            if key not in UNSUPPORTED_SERVICE_KEYS and value is not None
        }
        service["image"] = image
        resources = service.get("deploy", {}).get("resources", {})
        for resource_class in ("limits", "reservations"):
            resource_values = resources.get(resource_class, {})
            if "cpus" in resource_values:
                resource_values["cpus"] = str(resource_values["cpus"])

        legacy_name = original.get("container_name")
        aliases = [name]
        if legacy_name:
            aliases.append(legacy_name)
            legacy_containers[name] = legacy_name

        service["networks"] = {
            args.network: {
                "aliases": aliases,
            }
        }
        deploy = service.setdefault("deploy", {})
        deploy["replicas"] = 1
        deploy["update_config"] = {
            "parallelism": 1,
            "delay": "10s",
            "monitor": "45s",
            "failure_action": "rollback",
            "order": "start-first",
        }
        deploy["rollback_config"] = {
            "parallelism": 1,
            "delay": "5s",
            "monitor": "45s",
            "failure_action": "pause",
            "order": "stop-first",
        }
        deploy["restart_policy"] = {
            "condition": "on-failure",
            "delay": "5s",
            "max_attempts": 3,
            "window": "60s",
        }
        rendered_services[name] = service

    volumes = {}
    for name, config in source.get("volumes", {}).items():
        if isinstance(config, dict) and config.get("name"):
            volumes[name] = {"external": True, "name": config["name"]}

    output = {
        "services": rendered_services,
        "networks": {
            args.network: {
                "external": True,
                "name": args.network,
            }
        },
    }
    if volumes:
        output["volumes"] = volumes

    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    args.mapping_output.write_text(
        json.dumps(legacy_containers, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
