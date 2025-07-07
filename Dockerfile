# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code to the working directory
COPY . .

# Run uvicorn server
CMD ["uvicorn", "tts_api:app", "--host", "0.0.0.0", "--port", "8000"]
