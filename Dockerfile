# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies including MCP CLI
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir 'mcp[cli]'

# Copy source code
COPY src/ ./src/
COPY pyproject.toml .
COPY .env .

# Install the package
RUN pip install -e .

# Expose MCP Inspector ports
EXPOSE 6274 6277

# Run the MCP server in dev mode
CMD ["mcp", "dev", "src/bird_mcp/server.py"]
