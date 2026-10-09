# 📋 Hetzner Support Ticket Template — Netscan Whitelist Request

**Template for**: Hetzner Support Portal (https://support.hetzner.com/)

---

## Subject
```
Request: Whitelist IP 178.63.89.121 for GitHub Actions CI automation
```

## Description

```
Dear Hetzner Support,

We are using Hetzner infrastructure (server at 178.63.89.121) for production and 
continuous integration (GitHub Actions) automation.

**Issue**: During recent CI runs, our scanning activity triggered Hetzner's 
abuse detection system (netscan alert). This is legitimate CI automation traffic, 
not malicious activity.

**Details**:
- Server IP: 178.63.89.121
- Use case: GitHub Actions CI runner (automated testing, builds)
- Traffic type: 
  * DNS queries (yosys.org, github.com, crates.io, registry.npmjs.org)
  * Package manager connections (git clone, cargo fetch, pip install, npm install)
  * Artifact uploads (GitHub Actions)
  
**Expected behavior**: 
- CI runs: Daily, 2–6 runs per day
- Duration: 20–30 minutes per run (peaks: 15 concurrent connections)
- Outbound ports: 443 (HTTPS), 80 (HTTP), occasionally 22 (SSH)

**Request**:
Please whitelist IP 178.63.89.121 for CI automation traffic to prevent abuse 
alerts during legitimate GitHub Actions execution.

**Schedule**: No specific time window; CI runs on push to main branch (variable).

Thank you,
[Your Name]
Clisonix Cloud Operations
```

---

## Expected Response Time
- **SLA**: 1–2 business days (Hetzner standard)
- **Expedited**: Request in "Priority: Normal" category
- **Confirmation**: You'll receive email notification once whitelisted

## Follow-up Monitoring
Once whititelisted, verify:
```bash
# Monitor next CI run in GitHub Actions
# Should NOT see netscan alerts in CI logs or Hetzner dashboard
```

---

**Status**: Ready to submit upon user approval  
**Alternative**: Move CI to GitHub-hosted runners (Option B in analysis)
