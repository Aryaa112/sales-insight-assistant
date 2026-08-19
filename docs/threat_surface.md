# D4 — Threat Surface Map

| Component | Risk | Impact | Mitigation |
|---|---|---|---|
| Interface | Malicious input | System misuse | Input guardrail |
| Input Guardrail | Prompt injection | LLM manipulation | Rule-based detection |
| Input Guardrail | Jailbreak attempt | Safety bypass | Jailbreak pattern detection |
| Input Guardrail | PII in input | Sensitive data exposure | PII detection and redaction |
| LLM | Hallucinated SQL | Incorrect results | Schema-aware prompt |
| LLM | Dangerous SQL | Data modification | SQL validator |
| SQL Validator | Unknown table reference | Unauthorized data access | Allowed-table whitelist |
| Output Guardrail | Unsafe generated SQL | Database exposure | Re-validation before execution |
| Database | Excessive query results | Performance/resource issue | LIMIT 100 |
| Database | SQL execution failure | Incorrect response | Bounded retry |
| Result Sanitizer | Sensitive columns | Data exposure | Sensitive-column filtering |
| Result Layer | Empty result interpreted incorrectly | Misleading answer | Explicit empty-result handling |
| LLM Response | Biased or inconsistent answer | Poor business decision | RAI audit and transparency |