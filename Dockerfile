# Use Python 3.11 slim image
FROM python:3.11-slim

# Copy uv binary from the official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv (frozen lockfile if available)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project || uv sync --no-install-project

# Copy source code
COPY src/ ./src/

# Install the package
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen || uv sync

# Expose MCP Inspector ports
EXPOSE 6274 6277

# Run the MCP server directly (production mode)
CMD ["uv", "run", "python", "-m", "bird_mcp.server"]
