# Enterprise Core Python Library (`enterprise-core-python`)

Foundational enterprise starter library for Python Flask microservices providing:
- Structured JSON Logging with automated PII masking (credit cards, SSNs, bearer tokens, API keys)
- Unified RFC-7807 Error Envelope & centralized exception handling
- Microsecond latency tracking & `X-Correlation-ID` distributed tracing interceptor
- Spring Boot-style Actuators (`/health`, `/health/liveness`, `/health/readiness`, `/info`, `/metrics`)
- Reusable OpenAPI 3.0 & Swagger UI Blueprint with auto-injected actuator documentation
- Centralized dependency versions (Flask, urllib3, requests, gunicorn, etc.)

## Installation

```bash
pip install enterprise-core-python
```

Or install directly from GitHub tag/release:
```bash
# Public repo or with SSH:
pip install git+https://github.com/<OWNER>/enterprise-core-python.git@v1.0.0

# Private repo via Personal Access Token:
pip install git+https://${GITHUB_TOKEN}@github.com/<OWNER>/enterprise-core-python.git@v1.0.0
```
