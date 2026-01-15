# Main application entry point with FastAPI integration
from fastapi import FastAPI
from .config import get_settings
from .core import init_app

settings = get_settings()
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Initialize application with dependencies
init_app(app, settings)

# Health check endpoint
@app.get('/health')
def health_check():
    return {'status': 'healthy'}