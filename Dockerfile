# Multi-stage build for smaller final image
FROM python:3.13-slim AS builder

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --python /opt/venv/bin/python beautifulsoup4 pysocks requests

# Final stage - minimal runtime image
FROM python:3.13-slim

# Install make and other essential tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"

# Set environment variables
ENV PYTHONPATH=src
WORKDIR /app

# Copy application code and Makefile
COPY src /app/src
COPY Makefile /app/

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

CMD ["make", "docker-run"]