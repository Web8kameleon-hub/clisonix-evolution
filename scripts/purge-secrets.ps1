<#
Preview-or-execute helper for preparing replacements and showing git-filter-repo / BFG commands.
This script *does not* perform destructive changes unless called with `--execute`.

Usage:
  .\purge-secrets.ps1 --preview   # generate replacements.txt and show commands
  .\purge-secrets.ps1 --execute   # perform replacements (DANGEROUS)

#>
param(
    [switch]$Execute,
    [switch]$Preview
)

Set-StrictMode -Version Latest

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$replacements = Join-Path $root 'replacements.txt'

Write-Output "Generating replacements template at: $replacements"

$template = @(
    "# Replace common provider token patterns (review before executing)",
    "# Format: literal==>REDACTED", 
    "# Example: sk_live_123abc==>REDACTED",
    "# Common prefixes to replace (add more lines as needed):",
    "sk_live_==>REDACTED",
    "sk_test_==>REDACTED",
    "pk_live_==>REDACTED",
    "pk_test_==>REDACTED",
    "whsec_==>REDACTED",
    "PMAK-==>REDACTED",
    "github_pat_==>REDACTED",
    "linkedin_==>REDACTED",
    "EA-==>REDACTED"
)

$template | Out-File -FilePath $replacements -Encoding utf8

Write-Output "Prepared replacements template. Review $replacements and edit to include any exact tokens or substrings to replace."

$cmds = @(
    "# Using git-filter-repo (recommended)",
    "git clone --mirror <repo-url> repo-mirror.git",
    "cd repo-mirror.git",
    "git filter-repo --replace-text ../scripts/replacements.txt",
    "git push --force",
    "",
    "# Using BFG (alternate)",
    "bfg --replace-text ../scripts/replacements.txt repo.git",
    "cd repo.git",
    "git reflog expire --expire=now --all",
    "git gc --prune=now --aggressive",
    "git push --force"
)

Write-Output "Preview: the following commands show how to run the rewrite (DO NOT RUN unless ready):`n"
$cmds | ForEach-Object { Write-Output $_ }

if ($Execute)
{
    Write-Output "--EXECUTE flag passed. About to run destructive history rewrite. Make a backup and ensure you understand the implications.";
    throw "Automatic execution disabled in this helper for safety. Re-run the specific git-filter-repo command manually after reviewing replacements.txt."
}

Write-Output "Script complete. Edit replacements.txt and run the chosen command when ready."
