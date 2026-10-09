# Secrets Remediation & Rotation Guide

This document explains immediate steps to remediate leaked secrets, rotate them, and safely remove them from Git history.

IMPORTANT: Do NOT paste real secrets into public chat or issue trackers.

1) Immediate actions (rotate/revoke)
- For each leaked credential (Stripe, PayPal, Clerk, GitHub PAT, LinkedIn, Postman API key):
  - Go to the provider dashboard (Stripe/PayPal/Clerk/GitHub) and immediately revoke or rotate the key.
  - If a PAT or token cannot be rotated, delete it and create a new one.
  - Update your services/CI with new secrets via GitHub Secrets or your secrets manager.

2) Remove sensitive files from the repository (safe local steps)
- Ensure `.env` is in `.gitignore` (this repo already includes `.env` patterns).
- Replace any committed secret values with placeholders (we've already redacted `.env` in the repo).

3) Remove secret values from Git history (choose one preferred tool)
- Preferred: `git filter-repo` (fast and supported)
  - Install: `pip install git-filter-repo`
  - Example: to remove a file that contained secrets:
    ```bash
    git clone --mirror git@github.com:your/repo.git repo-mirror.git
    cd repo-mirror.git
    git filter-repo --invert-paths --paths .env
    git push --force
    ```
  - To replace a literal secret string across history, create `replacements.txt` with lines like:
    ```
    <REAL_SECRET_TOKEN>==>REDACTED
    ```
    Then run:
    ```bash
    git filter-repo --replace-text replacements.txt
    ```
- Alternate: BFG Repo-Cleaner
  - See BFG docs: https://rtyley.github.io/bfg-repo-cleaner/
  - Example:
    ```bash
    bfg --replace-text replacements.txt repo.git
    cd repo.git
    git reflog expire --expire=now --all
    git gc --prune=now --aggressive
    git push --force
    ```

4) Rotate secrets in your services
- For each service that used the old secret, update the runtime environment to the new secret and restart the service.
- In CI/CD (GitHub Actions): go to Repository → Settings → Secrets and variables → Actions and add the new secrets there.

5) Validate
- Run tests and smoke checks to confirm payments/auth flows work (use test keys in sandbox modes first).
- Confirm no secrets remain in the repo using `git log -S'<secret substring>'` or the `find_keys.ps1` script.

6) Prevent future leaks
- Add `.env` to `.gitignore` (already present).
- Add pre-commit hooks to block committing common secret patterns (e.g., detect `sk_live_` or `github_pat_` tokens). Example tools: `git-secrets`, `pre-commit` with `detect-secrets`.
- Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager, Azure Key Vault) for prod.

7) If you want help performing the cleanup
- I can prepare the `replacements.txt` and exact `git filter-repo` or BFG commands provided you confirm which secret placeholders to target (do NOT paste secrets in chat). Instead provide the token prefix (e.g. `sk_live_` or `github_pat_11`) and I will generate the commands.

---

If you want, I can now:
- Add pre-commit hooks and `detect-secrets` configuration.
- Generate the exact `git filter-repo` / BFG replacement commands using token prefixes.
- Provide a checklist to rotate all identified provider keys.

Prepared scripts: see `scripts/README` and the scripts in `scripts/` for preview and execute options.
