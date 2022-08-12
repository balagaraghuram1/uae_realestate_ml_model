"""OpenAPI documentation customizations."""
from fastapi.openapi.utils import get_openapi

def custom_openapi(app):
    """Generate customized OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description="Production ML platform for UAE real estate investment analytics. "
                    "Provides price prediction, demand forecasting, rental yield analysis, "
                    "and risk assessment for properties across all seven UAE emirates.",
        routes=app.routes,
    )
    schema["info"]["contact"] = {
        "name": "UAE Real Estate ML Team",
        "email": "support@uae-realestate-ml.com",
    }
    schema["info"]["license"] = {"name": "MIT", "url": "https://opensource.org/licenses/MIT"}
    schema["info"]["x-logo"] = {
        "url": "https://uae-realestate-ml.com/logo.png",
        "altText": "UAE Real Estate ML",
    }
    schema["tags"] = [
        {"name": "properties", "description": "Property search and listings"},
        {"name": "predictions", "description": "ML-powered predictions"},
        {"name": "analytics", "description": "Market analytics and insights"},
        {"name": "health", "description": "System health checks"},
    ]
    app.openapi_schema = schema
    return schema
