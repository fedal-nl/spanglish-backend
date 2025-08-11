# Use slim base image
FROM python:3.13-slim

# Install system dependencies (SQLite, build tools, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    gcc \
    vim \
    libsqlite3-dev \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy only dependency files first to cache installs
COPY pyproject.toml uv.lock ./

# Install dependencies with uv
RUN uv sync --frozen

# Copy rest of your application
COPY . .

# Expose port
EXPOSE 8000

# Run Django server on container start
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]