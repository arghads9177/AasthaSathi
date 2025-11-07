#!/bin/bash
# Start the AasthaSathi Streamlit UI

echo "🎨 Starting AasthaSathi Streamlit UI..."
echo "================================================"
echo ""
echo "UI will be available at:"
echo "  - Streamlit UI: http://localhost:8501"
echo ""
echo "Make sure the API server is running at http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the UI"
echo "================================================"
echo ""

# Start the Streamlit app
/home/argha-ds/datascience/ai-assistant/AasthaSathi/.venv/bin/streamlit run ui/app.py
