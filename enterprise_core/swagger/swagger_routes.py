"""
Enterprise Swagger and OpenAPI 3.0 Documentation Routes Blueprint Factory.
Mounted strictly under the service context path.
"""
import copy
from typing import Dict, Any
from flask import Blueprint, jsonify

ACTUATOR_OPENAPI_PATHS = {
    "/health": {
        "get": {
            "tags": ["Actuators"],
            "summary": "Overall system health and component status",
            "description": "Returns aggregated health status (UP/DEGRADED) along with status of critical subsystems.",
            "responses": {
                "200": {
                    "description": "System is healthy and fully operational"
                },
                "503": {
                    "description": "One or more critical subsystems are unhealthy or degraded"
                }
            }
        }
    },
    "/health/liveness": {
        "get": {
            "tags": ["Actuators"],
            "summary": "Kubernetes / Cloud Run liveness probe",
            "description": "Verifies that the process is running and responsive. Used by container orchestrators to determine if the container should be restarted.",
            "responses": {
                "200": {
                    "description": "Application process is alive"
                }
            }
        }
    },
    "/health/readiness": {
        "get": {
            "tags": ["Actuators"],
            "summary": "Kubernetes / Cloud Run readiness probe",
            "description": "Verifies that the application is fully ready to accept incoming production traffic.",
            "responses": {
                "200": {
                    "description": "Application is ready to accept traffic"
                },
                "503": {
                    "description": "Application is not yet ready to accept traffic"
                }
            }
        }
    },
    "/info": {
        "get": {
            "tags": ["Actuators"],
            "summary": "Application metadata and runtime information",
            "description": "Returns service name, application version, Python runtime info, and process uptime.",
            "responses": {
                "200": {
                    "description": "Application information"
                }
            }
        }
    },
    "/metrics": {
        "get": {
            "tags": ["Actuators"],
            "summary": "Basic operational metrics",
            "description": "Returns runtime metrics including memory consumption and process uptime.",
            "responses": {
                "200": {
                    "description": "Service metrics"
                }
            }
        }
    }
}

def create_swagger_blueprint(
    context_path: str,
    openapi_spec: Dict[str, Any],
    title: str = "Enterprise Microservice - Swagger UI",
    include_actuators: bool = True
) -> Blueprint:
    """
    Factory function creating an enterprise Swagger UI & OpenAPI Blueprint mounted under context_path.
    
    Endpoints provided:
    - GET {context_path}/swagger     -> Interactive Swagger UI HTML
    - GET {context_path}/openapi.json -> OpenAPI 3.0.3 specification JSON
    """
    bp = Blueprint("enterprise_swagger", __name__, url_prefix=context_path)
    openapi_url = f"{context_path}/openapi.json"

    # Deep-copy spec so caller's original dictionary is not mutated
    spec = copy.deepcopy(openapi_spec)
    if include_actuators:
        paths = spec.setdefault("paths", {})
        for path_key, path_item in ACTUATOR_OPENAPI_PATHS.items():
            if path_key not in paths:
                paths[path_key] = path_item

        tags = spec.setdefault("tags", [])
        tag_names = {t.get("name") for t in tags if isinstance(t, dict)}
        if "Actuators" not in tag_names:
            tags.append({
                "name": "Actuators",
                "description": "Spring Boot-style operational probes, health checks, and runtime metrics"
            })

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <link rel="icon" type="image/png" href="https://unpkg.com/swagger-ui-dist@5/favicon-32x32.png" sizes="32x32" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.onload = function() {{
        SwaggerUIBundle({{
          url: "{openapi_url}",
          dom_id: '#swagger-ui',
          presets: [SwaggerUIBundle.presets.apis]
        }});
      }};
    </script>
</body>
</html>"""

    @bp.route("/swagger", methods=["GET"])
    def swagger_ui():
        """Interactive Swagger UI HTML page."""
        return html, 200, {"Content-Type": "text/html"}

    @bp.route("/openapi.json", methods=["GET"])
    def serve_openapi_spec():
        """OpenAPI 3.0 specification JSON."""
        return jsonify(spec), 200

    return bp
