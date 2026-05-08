FROM python:3.11-slim

# Prevent Python from creating `.pyc` bytecode files inside the container.
ENV PYTHONDONTWRITEBYTECODE=1
# Flush Python output immediately so logs appear in real time.
ENV PYTHONUNBUFFERED=1

# Set the working directory used by the remaining Dockerfile commands.
WORKDIR /app

# Copy dependency definitions into the image first for better layer caching.
COPY requirements.txt .
# Install the Python packages required by the placeholder app.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the image.
COPY main.py .

# Document that the container listens on port 8000.
EXPOSE 8000

# Start the FastAPI app with Uvicorn when the container launches.
# Explain the command
# uvicorn is a ASGI server that runs the FastAPI application.
# main:app is the application to run.
# --host 0.0.0.0 is the host to listen on.
# --port 8000 is the port to listen on.
# This command starts the FastAPI application on port 8000.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
