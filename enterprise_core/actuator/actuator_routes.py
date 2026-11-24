"""
Enterprise Spring Boot-Style Actuators and Operational Health Probes Blueprint Factory.
Mounted strictly under the service context path.
"""
import time
import sys
from datetime import datetime, timezone
from typing import Callable, Optional, Dict, Any, Tuple
from flask import Blueprint, jsonify

def create_actuators_blueprint(
    context_path: str,
    service_name: str,
    version: str = "1.0.0",
    health_callback: Optional[Callable[[], Tuple[bool, Dict[str, Any]]]] = None,
    readiness_callback: Optional[Callable[[], Tuple[bool, Optional[str]]]] = None
) -> Blueprint:
    """
    Factory function creating an enterprise actuators Blueprint mounted under context_path.
    
    Endpoints provided:
    - GET {context_path}/health
    - GET {context_path}/health/liveness
    - GET {context_path}/health/readiness
    - GET {context_path}/info
    - GET {context_path}/metrics
    """
    bp = Blueprint("enterprise_actuators", __name__, url_prefix=context_path)
    start_time = time.time()

    @bp.route("/health", methods=["GET"])
    def health():
        """System health status with component readiness."""
        components = {"diskSpace": {"status": "UP"}}
        is_healthy = True

        if health_callback:
            try:
                cb_healthy, custom_components = health_callback()
                is_healthy = cb_healthy
                components.update(custom_components)
            except Exception as ex:
                is_healthy = False
                components["customCheck"] = {"status": "DOWN", "error": str(ex)}

        payload = {
            "status": "UP" if is_healthy else "DEGRADED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contextPath": context_path,
            "components": components
        }
        return jsonify(payload), (200 if is_healthy else 503)

    @bp.route("/health/liveness", methods=["GET"])
    def liveness():
        """Liveness probe for Cloud Run / Kubernetes."""
        return jsonify({"status": "UP", "probe": "liveness"}), 200

    @bp.route("/health/readiness", methods=["GET"])
    def readiness():
        """Readiness probe for Cloud Run / Kubernetes."""
        is_ready = True
        reason = None

        if readiness_callback:
            try:
                is_ready, reason = readiness_callback()
            except Exception as ex:
                is_ready = False
                reason = str(ex)

        if is_ready:
            return jsonify({"status": "UP", "probe": "readiness"}), 200
        
        payload = {"status": "OUT_OF_SERVICE", "probe": "readiness"}
        if reason:
            payload["reason"] = reason
        return jsonify(payload), 503

    @bp.route("/info", methods=["GET"])
    def info():
        """Service metadata, runtime version, and uptime."""
        return jsonify({
            "app": {
                "name": service_name,
                "version": version,
                "contextPath": context_path
            },
            "python": {
                "version": sys.version,
                "runtime": f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            },
            "uptimeSeconds": round(time.time() - start_time, 2)
        }), 200

    @bp.route("/metrics", methods=["GET"])
    def metrics():
        """Basic operational metrics."""
        return jsonify({
            "uptimeSeconds": round(time.time() - start_time, 2),
            "status": "UP",
            "service": service_name
        }), 200

    return bp
