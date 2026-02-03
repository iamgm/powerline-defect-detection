#!/bin/bash

# запускаем FastAPI в фоновом режиме  на порту 8000
echo "🚀 Starting FastAPI Backend..."
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

# ждем пару секунд, чтобы сервер успел подняться
sleep 5

# запускаем Streamlit на порту 7860 (Требование Hugging Face)
echo "🚀 Starting Streamlit Frontend..."
streamlit run src/ui/app.py --server.port 7860 --server.address 0.0.0.0