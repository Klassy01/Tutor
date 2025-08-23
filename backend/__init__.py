"""Application initialization."""

# Import main app 
try:
    from backend.main import app
    __all__ = ["app"]
except ImportError:
    # Fallback in case of import issues
    app = None
    __all__ = []
