"""
orchestra__main__
==================
Allow running as:  python -m orchestra
"""
import asyncio
import json
import logging
import sys

logging.basicConfig(level="INFO", format="%(levelname)s %(name)s — %(message)s")

from orchestra import OrchestraDivision


async def _main() -> int:
    """CLI entry-point: runs all probes and prints JSON report."""
    domains = sys.argv[1:] if len(sys.argv) > 1 else None
    async with OrchestraDivision(domains=domains) as division:
        report = await division.run()

    data = report.to_dict()
    print(json.dumps(data, indent=2))

    # exit 1 on error
    return 1 if data["overall"] == "error" else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(_main()))
