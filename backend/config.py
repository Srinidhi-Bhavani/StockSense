"""
StockSense — Central Configuration
Reads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path

# Resolve the project root (two levels up from this file: backend/ -> StockSense/)
_BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# Default: SQLite stored inside the /database folder at the project root.
# Override by setting DATABASE_URL in your environment or a .env file.
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{_BASE_DIR / 'database' / 'stocksense.db'}"
)

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
API_PREFIX: str = "/api/v1"
PROJECT_NAME: str = "StockSense"
VERSION: str = "1.0.0"
DESCRIPTION: str = (
    "StockSense Inventory Management API — "
    "Odoo x GCET Hyderabad Hackathon 2026"
)

# ---------------------------------------------------------------------------
# CORS — allow all origins during development
# ---------------------------------------------------------------------------
CORS_ORIGINS: list[str] = ["*"]
