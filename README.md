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

Or from private GitHub Packages:
```bash
pip install enterprise-core-python --extra-index-url https://pypi.pkg.github.com/<OWNER>/simple
```
