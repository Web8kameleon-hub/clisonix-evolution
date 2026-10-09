# ISO 27001 Scope and Boundary

Date: 2026-05-09
Owner: [insert]

## 1. Organization Scope
- Legal entity: [insert]
- Locations: [insert]
- Business functions included: AI services, API platform, operational monitoring, deployment workflows

## 2. Technical Scope
- In-scope services:
  - CLX core runtime
  - CLX.I service
  - Supporting API and deployment services
- In-scope environments:
  - Production
  - Staging
  - Critical CI/CD systems

## 3. Assets in Scope
- Source code repositories
- Runtime configuration and environment variables
- Logs, telemetry, monitoring data
- Build and release artifacts
- Credentials and secrets management systems

## 4. Exclusions (with rationale)
- [insert exclusions and business/technical justification]

## 5. Interfaces and Dependencies
- Cloud and hosting providers
- Upstream model providers/services
- Monitoring and alerting stack
- Payment/identity integrations where relevant

## 6. Interested Parties
- Customers
- Regulators
- Internal engineering and operations
- External auditors/certification body

## 7. Information Security Objectives (initial)
1. Prevent unauthorized access to production systems.
2. Ensure traceable and tamper-evident operational logging.
3. Maintain secure change and deployment control.
4. Ensure incident detection and response within defined SLA.
