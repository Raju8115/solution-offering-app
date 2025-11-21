# Solution Offering API

FastAPI backend for Solution Offering application with TiDB database and IBM W3 Authentication.

## Features

- FastAPI framework
- SQLAlchemy ORM
- Alembic migrations
- IBM AppID (W3) authentication
- Comprehensive API endpoints
- CORS enabled

## Prerequisites

- Python 3.9+
- IBM AppID credentials

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000