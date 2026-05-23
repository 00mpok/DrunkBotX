# Use official Python image for version 3.13
FROM python:3.13

# Set working directory inside the container
WORKDIR /app

# Copy dependencies
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire source code
COPY app/ /app/

# Command to run the bot
CMD ["python3", "bot.py"]
