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
RUN uv sync --frozen --no-dev

# Final stage - minimal runtime image
FROM python:3.13-slim

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set environment variables
ENV PYTHONPATH=src
WORKDIR /app

# Copy application code and Makefile
COPY src /app/src
COPY Makefile /app/

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

CMD ["make", "run"]