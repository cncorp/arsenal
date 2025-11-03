FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create symlink for CLI (source will be mounted at /app/src)
RUN ln -sf /app/src/cli.py /usr/local/bin/code-search

CMD ["tail", "-f", "/dev/null"]