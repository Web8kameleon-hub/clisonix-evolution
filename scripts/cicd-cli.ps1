param(
  [string]$Message = "chore: automated deploy",
  [string]$Branch = "main",
  [string]$Workflow = "🚦 Auto Deploy (All Green)",
  [string]$Services = "web",
  [string]$EnvFile = ".env",
  [switch]$NoDeploy,
  [switch]$NoCommit,
  [switch]$NoPush
)

$ErrorActionPreference = "Stop"

function Step($text) {
  Write-Host "`n==> $text" -ForegroundColor Cyan
}

Step "Checking git repository state"
git rev-parse --is-inside-work-tree | Out-Null

$status = git status --porcelain

if (-not $NoCommit) {
  if ($status) {
    Step "Creating commit"
    git add -A
    git commit -m $Message
  }
  else {
    Write-Host "No local changes to commit." -ForegroundColor Yellow
  }
}

if (-not $NoPush) {
  Step "Pushing branch"
  git push origin $Branch
}

if ($NoDeploy) {
  Write-Host "Deploy step skipped (--NoDeploy)." -ForegroundColor Yellow
  exit 0
}

Step "Triggering GitHub Actions deploy workflow"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  Write-Host "GitHub CLI (gh) is not installed. Install from: https://cli.github.com/" -ForegroundColor Red
  Write-Host "Manual trigger command:" -ForegroundColor Yellow
  Write-Host "gh workflow run `"$Workflow`" --ref $Branch -f services=$Services"
  exit 1
}

gh auth status | Out-Null
gh workflow run "$Workflow" --ref $Branch -f services=$Services -f env_file=$EnvFile

Step "Workflow triggered"
Write-Host "Use this to follow progress:" -ForegroundColor Green
Write-Host "gh run list --workflow `"$Workflow`" --limit 5"
Write-Host "gh run watch"
