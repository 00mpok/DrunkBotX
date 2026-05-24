# Use official Python image for version 3.13
FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory inside the container
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Create non-root user in image
RUN useradd --no-create-home --uid 1000 drunkbot
USER drunkbot

# Copy the entire source code
COPY app/ /app/

# Command to run the bot
CMD ["/app/.venv/bin/python3", "bot.py"]