# Use a lightweight Python base image (pinned to bookworm for stability)
FROM python:3.9-slim-bookworm

# Set working directory to project root
WORKDIR /app

# Install system dependencies required for OpenCV
# libgl1 is the modern replacement for libgl1-mesa-glx in newer Debian
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# No-cache-dir keeps the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Create directory for artifacts if it doesn't exist (safety check)
RUN mkdir -p artifacts/classification

# Expose the port that Hugging Face Spaces uses by default (7860)
# or standard 8000 for other services
EXPOSE 7860

# Command to run the application
# We use host 0.0.0.0 to allow external access
# We use port 7860 for compatibility with Hugging Face Spaces
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
