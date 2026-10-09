#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

MAKE_CMD=""
if command -v make >/dev/null 2>&1; then
	MAKE_CMD="make"
elif command -v mingw32-make >/dev/null 2>&1; then
	MAKE_CMD="mingw32-make"
else
	echo "missing build tool: install make (or mingw32-make) to run simulations locally"
	exit 2
fi

if [ ! -f "firmware/firmware.hex" ]; then
	echo "[prep] firmware.hex missing, creating minimal placeholder for ROM load"
	mkdir -p firmware
	cat > firmware/firmware.hex <<'HEX'
@00000000
00000013
HEX
fi

echo "[1/3] Running simulation regression"
"$MAKE_CMD" -C tests clean run

echo "[2/3] Generating VCD toggle coverage summary"
"$MAKE_CMD" -C tests coverage

echo "[3/3] Running bounded formal checks"
yosys -q -s formal/kloud_bridge_formal.ys

echo "Verification passed: simulation + coverage + formal"
