#!/bin/bash

# Create and activate virtual environment (optional)
# python -m venv venv
# source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run FastAPI development server with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
