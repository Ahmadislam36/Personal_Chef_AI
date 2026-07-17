FROM python:3.11-slim

WORKDIR /app

# System deps (kept minimal; add build-essential etc. only if a package needs it)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Railway injects PORT at runtime; Streamlit must bind to it
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8080

CMD streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0
