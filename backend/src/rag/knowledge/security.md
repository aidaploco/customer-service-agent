# Brightloop — Security and Compliance

## Data Security

All data in transit is encrypted with TLS 1.2 or higher. Data at rest is encrypted using AES-256. Encryption keys are managed via a cloud KMS with automatic annual rotation.

Event payloads are stored in Brightloop's infrastructure only long enough to fulfill your retention policy (7, 30, or 90 days depending on plan). You can trigger immediate deletion via the API or dashboard.

## Compliance

**SOC 2 Type II:** Brightloop is SOC 2 Type II certified. Enterprise customers can request the full audit report under NDA by contacting security@brightloop.io.

**GDPR:** Brightloop acts as a data processor under GDPR. A Data Processing Agreement (DPA) is available to all customers. Enterprise customers receive a countersigned DPA automatically.

**HIPAA:** Brightloop does not currently offer a BAA for HIPAA-covered workloads. If this is a requirement, contact sales to discuss roadmap timing.

## Network Security

Brightloop operates entirely within private cloud VPCs. All internal service communication is private. No event data traverses the public internet except for the final delivery leg to your endpoint.

IP allowlisting: Brightloop publishes a static list of egress IP ranges for customers who want to allowlist inbound webhook traffic. The list is available at brightloop.io/ip-ranges and updated with 30-day notice before any changes.

## Vulnerability Disclosure

Brightloop maintains a responsible disclosure program. Security researchers can report vulnerabilities to security@brightloop.io. We target a 90-day fix cycle for critical findings.

## Access Control

Role-based access control (RBAC) is available on Pro and Enterprise plans. Supported roles: Owner, Admin, Developer, Read-only. Enterprise plans include SSO via SAML 2.0.
