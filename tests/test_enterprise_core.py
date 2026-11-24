"""
Unit Tests for enterprise-core-python shared library.
Verifies error handlers, PII masking logger, latency interceptor, actuators, and Swagger factory.
"""
import pytest
from flask import Flask, jsonify
from werkzeug.exceptions import NotFound

from enterprise_core import (
    BaseEnterpriseException,
    register_centralized_error_handlers,
    PIIMaskingFilter,
    JsonLogFormatter,
    register_latency_interceptors,
    create_actuators_blueprint,
    create_swagger_blueprint
)

class SampleDomainException(BaseEnterpriseException):
    def __init__(self, item_id: str):
        super().__init__(
            error_code="SAMPLE_001",
            error_message="Sample entity not found",
            error_detail_message=f"Entity with ID {item_id} does not exist in store",
            status_code=404,
            details=["Verify entity ID"]
        )

@pytest.fixture
def test_app():
    app = Flask(__name__)
    register_latency_interceptors(app)
    register_centralized_error_handlers(app, default_internal_error_code="TEST_500", default_internal_error_msg="Test error")
    
    # Actuators
    act_bp = create_actuators_blueprint(
        context_path="/test-service",
        service_name="test-service",
        version="1.0.0",
        health_callback=lambda: (True, {"database": {"status": "UP"}}),
        readiness_callback=lambda: (True, None)
    )
    app.register_blueprint(act_bp)

    # Swagger
    sample_spec = {"openapi": "3.0.3", "info": {"title": "Test API", "version": "1.0.0"}}
    swg_bp = create_swagger_blueprint(
        context_path="/test-service",
        openapi_spec=sample_spec,
        title="Test API - Swagger UI"
    )
    app.register_blueprint(swg_bp)

    @app.route("/test-service/domain-error")
    def trigger_domain_error():
        raise SampleDomainException("123")

    @app.route("/test-service/unhandled-error")
    def trigger_unhandled_error():
        raise ValueError("Unexpected calculation bug")

    @app.route("/test-service/success")
    def trigger_success():
        return jsonify({"message": "OK"}), 200

    return app

@pytest.fixture
def client(test_app):
    return test_app.test_client()

def test_interceptor_propagates_correlation_id_and_latency(client):
    response = client.get("/test-service/success", headers={"X-Correlation-ID": "test-corr-456"})
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == "test-corr-456"
    assert "X-Response-Time-Ms" in response.headers
    assert float(response.headers["X-Response-Time-Ms"]) >= 0.0

def test_domain_exception_handling(client):
    response = client.get("/test-service/domain-error", headers={"X-Correlation-ID": "err-corr-1"})
    assert response.status_code == 404
    data = response.get_json()
    assert data["errorCode"] == "SAMPLE_001"
    assert data["errorMessage"] == "Sample entity not found"
    assert data["correlationId"] == "err-corr-1"
    assert data["status"] == 404
    assert "details" in data

def test_unhandled_exception_handling(client):
    response = client.get("/test-service/unhandled-error")
    assert response.status_code == 500
    data = response.get_json()
    assert data["errorCode"] == "TEST_500"
    assert data["status"] == 500

def test_http_exception_handling(client):
    response = client.get("/test-service/non-existent-path")
    assert response.status_code == 404
    data = response.get_json()
    assert data["errorCode"] == "HTTP_404"
    assert data["status"] == 404

def test_actuator_health(client):
    response = client.get("/test-service/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"
    assert data["components"]["database"]["status"] == "UP"
    assert data["components"]["diskSpace"]["status"] == "UP"

def test_actuator_liveness_and_readiness(client):
    liv = client.get("/test-service/health/liveness")
    assert liv.status_code == 200
    assert liv.get_json()["probe"] == "liveness"

    read = client.get("/test-service/health/readiness")
    assert read.status_code == 200
    assert read.get_json()["probe"] == "readiness"

def test_actuator_info_and_metrics(client):
    info = client.get("/test-service/info")
    assert info.status_code == 200
    assert info.get_json()["app"]["name"] == "test-service"

    metrics = client.get("/test-service/metrics")
    assert metrics.status_code == 200
    assert "uptimeSeconds" in metrics.get_json()

def test_swagger_ui_and_openapi_spec(client):
    ui = client.get("/test-service/swagger")
    assert ui.status_code == 200
    assert "SwaggerUIBundle" in ui.data.decode("utf-8")

    spec = client.get("/test-service/openapi.json")
    assert spec.status_code == 200
    spec_data = spec.get_json()
    assert spec_data["openapi"] == "3.0.3"
    assert "/health" in spec_data["paths"]
    assert "/health/liveness" in spec_data["paths"]
    assert "/health/readiness" in spec_data["paths"]
    assert "/info" in spec_data["paths"]
    assert "/metrics" in spec_data["paths"]

def test_pii_masking_filter():
    pii = PIIMaskingFilter()
    raw = "User email user@test.com with card 1234-5678-9012-3456 and token Bearer eyJhbGciOi..."
    masked = pii.mask_text(raw)
    assert "user[at]***.com" in masked
    assert "****-****-****-XXXX" in masked
    assert "Bearer [REDACTED_TOKEN]" in masked
