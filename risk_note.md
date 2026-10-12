1. Author & Provenance: Authored by the internal Support Operations engineering team (support-ops@internal) as a quick-turnaround integration service.
2. Data & System Reach: Directly reaches production Zendesk/Jira customer ticket stores, private agent notes, full CRM customer profiles, and escalation queues.
3. Telemetry & Audit Logs: Logs plaintext ticket IDs, customer email identifiers, and response payload byte counts to unencrypted local stdout/syslog without PII redaction.
4. Blast Radius of Stolen Token: Enables full exfiltration of sensitive escalation history, internal fraud suspicion notes, and customer account records across the entire enterprise.
5. Production Verdict: DO NOT SHIP until token-scoped RBAC, per-tenant authorization boundaries, mutual TLS, and automated PII scrubbing are enforced.
