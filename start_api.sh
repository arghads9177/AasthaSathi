#!/bin/bash
# Start the AasthaSathi API server

echo "🚀 Starting AasthaSathi API Server..."
echo "================================================"
echo ""
echo "API will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/api/v1/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================"
echo ""

# Start the server
/home/argha-ds/datascience/ai-assistant/AasthaSathi/.venv/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
