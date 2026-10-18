
# UltraWebThinking - Advanced Orchestrator Script (all.ps1)
# Ky skript ndez të gjitha node-t kryesore në terminale të ndara, kontrollon varësitë dhe logon statusin

function Start-Node {
	param(
		[string]$Path,
		[string]$Command,
		[string]$Name
	)
	Write-Host "[INFO] Kontrolloj varësitë për $Name..."
	if (Test-Path "$Path/yarn.lock") {
		Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd $Path; if (!(Test-Path node_modules)) { yarn install --immutable }; $Command"
	} elseif (Test-Path "$Path/package.json") {
		Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd $Path; if (!(Test-Path node_modules)) { npm install --legacy-peer-deps }; $Command"
	} elseif (Test-Path "$Path/pyproject.toml") {
		Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd $Path; if (!(Test-Path .venv)) { python -m venv .venv; .venv\\Scripts\\pip install -r requirements.txt }; $Command"
	} else {
		Write-Host "[WARN] Nuk u gjetën varësi për $Name. Niset vetëm komanda."
		Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd $Path; $Command"
	}
	Write-Host "[OK] $Name u nis."
}

# Start Frontend (Next.js/React)
Start-Node "../frontend" "yarn dev" "Frontend (Next.js)"

# Start Backend (Node.js/FastAPI)
Start-Node "../backend" "yarn dev" "Backend (Node.js)"

# Start AGISheet (TypeScript)
Start-Node "../agisheet" "yarn dev" "AGISheet"

# Start Mesh Node
Start-Node "../mesh" "yarn dev" "Mesh Node"

# Start UTT Node
Start-Node "../utt" "yarn dev" "UTT Node"

# Start DDoS Node
Start-Node "../ddos" "yarn dev" "DDoS Node"

# Start Governance Node
Start-Node "../governance" "yarn dev" "Governance Node"

# Shto këtu node të tjerë sipas nevojës

Write-Host 'Të gjitha node-t kryesore janë ndezur në terminale të ndara.'