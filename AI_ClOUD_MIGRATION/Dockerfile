# Dockerfile for AI Cloud Migration Copilot Streamlit dashboard
# Uses a lightweight Python runtime and installs dependencies from requirements.txt.

FROM python:3.12-slim as base

# Create a non-root user for better security
RUN useradd --create-home appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_PORT=8501 \
    PYTHONUNBUFFERED=1

# Expose Streamlit default port
EXPOSE 8501

# Run the application
USER appuser
CMD ["python", "run.py"]
