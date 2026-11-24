# Enterprise Core Python Library (`enterprise-core-python`)

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-3.1.0-green.svg)](https://palletsprojects.com/p/flask/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-Internal%20Enterprise-lightgrey.svg)]()

Foundational enterprise shared library for Python Flask microservices providing standard cross-cutting concerns:
- **Centralized Exception Handling & Generic Error Envelope** (RFC 7807 aligned)
- **Structured JSON Logging with Automated PII Masking** (credit cards, accounts, emails, bearer tokens)
- **End-to-End Latency Tracking & `X-Correlation-ID` Distributed Tracing Interceptors**
- **Spring Boot-Style Actuators** (`/health`, `/health/liveness`, `/health/readiness`, `/info`, `/metrics`)
- **OpenAPI 3.0 & Swagger UI Blueprint Factory** with automatic Actuator spec injection
- **Centralized Dependency Management (BOM)** for Flask, Requests, Pytest, Gunicorn, and Waitress

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Features & Modules](#core-features--modules)
  - [1. Centralized Error Handling & Generic Error Envelope](#1-centralized-error-handling--generic-error-envelope)
  - [2. Structured JSON Logging & PII Masking](#2-structured-json-logging--pii-masking)
  - [3. Correlation Tracking & Latency Interceptor](#3-correlation-tracking--latency-interceptor)
  - [4. Spring Boot-Style Actuators](#4-spring-boot-style-actuators)
  - [5. OpenAPI 3.0 & Swagger UI Blueprint](#5-openapi-30--swagger-ui-blueprint)
- [Centralized Dependency BOM](#centralized-dependency-bom)
- [Local Development & Testing](#local-development--testing)
- [Release Workflow](#release-workflow)

---

## Installation

### From GitHub Release / Git Tag
You can install `enterprise-core-python` directly using `pip`:

```bash
# Public repository or using SSH:
pip install git+https://github.com/<OWNER>/enterprise-core-python.git@v1.0.0

# Private repository via Personal Access Token (PAT):
pip install git+https://${GITHUB_TOKEN}@github.com/<OWNER>/enterprise-core-python.git@v1.0.0
```

### With Optional Dependencies (e.g., AWS Boto3)
```bash
pip install "enterprise-core-python[aws] @ git+https://github.com/<OWNER>/enterprise-core-python.git@v1.0.0"
```

### Local Editable Installation (Development)
```bash
git clone https://github.com/<OWNER>/enterprise-core-python.git
cd enterprise-core-python
pip install -e .
```

---

## Quick Start

Here is a complete, production-ready Flask microservice integrating all enterprise capabilities:

```python
from flask import Flask, jsonify
from enterprise_core import (
    setup_enterprise_logging,
    register_latency_interceptors,
    register_centralized_error_handlers,
    create_actuators_blueprint,
    create_swagger_blueprint,
    BaseEnterpriseException,
)

# 1. Initialize Structured JSON Logging with PII Scrubbing
setup_enterprise_logging(service_name="account-service", log_level="INFO")

# 2. Instantiate Flask App
app = Flask(__name__)
CONTEXT_PATH = "/api/v1/accounts"

# 3. Register Latency Tracking & Correlation Tracing (X-Correlation-ID)
register_latency_interceptors(app)

# 4. Register Centralized Error Handling (Unified Error Envelope)
register_centralized_error_handlers(
    app,
    default_internal_error_code="ACCOUNT_500",
    default_internal_error_msg="An unexpected error occurred in Account Service."
)

# 5. Mount Spring Boot-style Actuators (/health, /liveness, /readiness, /info, /metrics)
actuator_bp = create_actuators_blueprint(
    context_path=CONTEXT_PATH,
    service_name="account-service",
    version="1.0.0",
    health_callback=lambda: (True, {"database": {"status": "UP"}}),
    readiness_callback=lambda: (True, None)
)
app.register_blueprint(actuator_bp)

# 6. Mount Swagger UI & OpenAPI 3.0 Specs (/swagger, /openapi.json)
openapi_spec = {
    "openapi": "3.0.3",
    "info": {"title": "Account Service API", "version": "1.0.0"}
}
swagger_bp = create_swagger_blueprint(
    context_path=CONTEXT_PATH,
    openapi_spec=openapi_spec,
    title="Account Service - API Documentation"
)
app.register_blueprint(swagger_bp)

# 7. Business Route
@app.route(f"{CONTEXT_PATH}/<account_id>", methods=["GET"])
def get_account(account_id):
    if account_id == "404":
        raise BaseEnterpriseException(
            error_code="ACC_NOT_FOUND",
            error_message="Account does not exist",
            error_detail_message=f"No account record found for ID: {account_id}",
            status_code=404,
            details=["Verify account ID format"]
        )
    return jsonify({"accountId": account_id, "balance": 1500.00}), 200

if __name__ == "__main__":
    app.run(port=8080)
```

---

## Core Features & Modules

### 1. Centralized Error Handling & Generic Error Envelope

Standardizes exception responses across all Python microservices into a single, predictable JSON format with HTTP status codes and `X-Correlation-ID` response headers.

#### Custom Domain Exceptions
Subclass `BaseEnterpriseException` for business domain errors:

```python
from enterprise_core import BaseEnterpriseException

class InsufficientFundsException(BaseEnterpriseException):
    def __init__(self, account_id: str, balance: float, required: float):
        super().__init__(
            error_code="INSUFFICIENT_FUNDS",
            error_message="Account has insufficient balance",
            error_detail_message=f"Account {account_id} balance ${balance} is less than required ${required}",
            status_code=422,
            details=["Deposit funds or reduce transaction amount"]
        )
```

#### Standard Error Response Envelope
Whether triggered by a `BaseEnterpriseException`, a Werkzeug `HTTPException` (e.g. 404, 405), or an unhandled 500 error, all responses follow this structure:

```json
{
  "timestamp": "2026-11-24T11:45:00.123456+00:00",
  "status": 404,
  "errorCode": "ACC_NOT_FOUND",
  "errorMessage": "Account does not exist",
  "errorDetailMessage": "No account record found for ID: 999",
  "path": "/api/v1/accounts/999",
  "correlationId": "4bf92f35-77b3-40cf-a73c-3e3c0428db0a",
  "details": [
    "Verify account ID format"
  ]
}
```

---

### 2. Structured JSON Logging & PII Masking

Configures standard stdout logging in machine-readable JSON format, enriched with request context, and scrubs sensitive Personally Identifiable Information (PII) before it is printed or shipped.

```python
from enterprise_core import setup_enterprise_logging

setup_enterprise_logging(service_name="payment-service", log_level="INFO")
```

#### Automatic PII Scrubbing
The built-in `PIIMaskingFilter` automatically redacts sensitive data from log messages, arguments, and dictionaries:
* **Email addresses:** `john.doe@company.com` $\rightarrow$ `john.doe[at]***.com`
* **Credit Card Numbers:** `4532 1234 5678 9012` $\rightarrow$ `****-****-****-XXXX`
* **Account Numbers (9–18 digits):** `123456789012` $\rightarrow$ `***ACCOUNT***`
* **Bearer Tokens / API Keys:** `Bearer eyJhbGci...` $\rightarrow$ `Bearer [REDACTED_TOKEN]`

#### JSON Log Format Example
```json
{
  "timestamp": "2026-11-24T11:45:00.123456+00:00",
  "level": "INFO",
  "service": "payment-service",
  "correlationId": "4bf92f35-77b3-40cf-a73c-3e3c0428db0a",
  "logger": "access_audit",
  "message": "Request completed: GET /api/v1/accounts/123 -> 200 in 2.34ms",
  "module": "latency_interceptor",
  "lineno": 47,
  "method": "GET",
  "path": "/api/v1/accounts/123",
  "status_code": 200,
  "duration_ms": 2.34
}
```

---

### 3. Correlation Tracking & Latency Interceptor

The latency interceptor manages distributed tracing context and performance telemetry on every HTTP request:

```python
from enterprise_core import register_latency_interceptors

register_latency_interceptors(app)
```

* **`X-Correlation-ID` Propagation:** Extracts `X-Correlation-ID` from incoming request headers or generates a new `UUIDv4`. Stores it in Flask's request-scoped `g.correlation_id` and attaches it to the response header.
* **`X-Response-Time-Ms` Header:** Computes high-precision response duration with `time.perf_counter()` and returns the elapsed time in milliseconds.
* **Audit Logging:** Automatically logs an `access_audit` entry with method, path, HTTP status, correlation ID, and latency.

---

### 4. Spring Boot-Style Actuators

Exposes operational endpoints mounted strictly under the service's `context_path`:

```python
from enterprise_core import create_actuators_blueprint

actuator_bp = create_actuators_blueprint(
    context_path="/api/v1/accounts",
    service_name="account-service",
    version="1.0.0",
    health_callback=lambda: (True, {"postgres": {"status": "UP"}, "redis": {"status": "UP"}}),
    readiness_callback=lambda: (True, None)
)
app.register_blueprint(actuator_bp)
```

| Endpoint | Method | Purpose | Typical Response |
| :--- | :---: | :--- | :--- |
| `{context_path}/health` | `GET` | Aggregated health check (UP / DEGRADED) | `200 OK` or `503 Service Unavailable` |
| `{context_path}/health/liveness` | `GET` | Kubernetes / Cloud Run liveness probe | `200 OK` (`{"status":"UP","probe":"liveness"}`) |
| `{context_path}/health/readiness` | `GET` | Kubernetes / Cloud Run readiness probe | `200 OK` or `503 Service Unavailable` |
| `{context_path}/info` | `GET` | Application metadata, Python runtime, uptime | `200 OK` |
| `{context_path}/metrics` | `GET` | Uptime and operational metrics | `200 OK` |

---

### 5. OpenAPI 3.0 & Swagger UI Blueprint

Serves an interactive Swagger UI documentation portal and raw OpenAPI 3.0 JSON specification under the service's context path.

```python
from enterprise_core import create_swagger_blueprint

swagger_bp = create_swagger_blueprint(
    context_path="/api/v1/accounts",
    openapi_spec=my_service_openapi_spec,
    title="Account Service - Swagger UI",
    include_actuators=True  # Automatically adds /health, /info, /metrics to Swagger docs
)
app.register_blueprint(swagger_bp)
```

* **Swagger UI HTML:** Accessible at `GET {context_path}/swagger`
* **Raw OpenAPI Spec:** Accessible at `GET {context_path}/openapi.json`
* **Auto-Injected Actuators:** Automatically injects the documentation and schemas for all actuator endpoints into the spec under the `Actuators` tag.

---

## Centralized Dependency BOM

`enterprise-core-python` acts as an enterprise Bill of Materials (BOM), pinning compatible, security-audited versions across Python services:

| Dependency | Version | Purpose |
| :--- | :--- | :--- |
| **Flask** | `3.1.0` | Core WSGI web framework |
| **werkzeug** | `3.1.3` | WSGI utility library and HTTP primitives |
| **python-json-logger** | `2.0.7` | Base JSON log parsing |
| **requests** | `2.32.3` | HTTP client for outbound calls |
| **urllib3** | `2.2.3` | Low-level HTTP transport |
| **gunicorn** | `23.0.0` | Linux production WSGI HTTP server |
| **waitress** | `3.0.1` | Cross-platform / Windows WSGI HTTP server |
| **pytest** | `8.3.3` | Test runner framework |
| **boto3** *(optional)* | `1.35.40` | AWS SDK (`enterprise-core-python[aws]`) |

---

## Local Development & Testing

### Running Tests
Execute the comprehensive test suite with `pytest`:

```bash
pytest tests/ -v
```

### Building the Package
To build distribution packages (`.whl` and `.tar.gz`):

```bash
python -m build
twine check dist/*
```

---

## Release Workflow

When changes are merged and tagged with semantic versioning:

```bash
git tag v1.0.1
git push origin v1.0.1
```

The GitHub Actions workflow in [`.github/workflows/release.yml`](.github/workflows/release.yml) will automatically:
1. Run test suite across dependencies.
2. Build wheel distribution (`.whl`) and source archive (`.tar.gz`).
3. Validate metadata via `twine check`.
4. Create a new **GitHub Release** and attach the build artifacts for distribution.
