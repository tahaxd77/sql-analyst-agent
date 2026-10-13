FROM python:3.11-slim

WORKDIR /workspace

# Prevent Python from writing .pyc and enable bufferless logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose API (8000) and Streamlit (8501)
EXPOSE 8000 8501

CMD ["uvicorn", "app.api.main:api", "--host", "0.0.0.0", "--port", "8000"]