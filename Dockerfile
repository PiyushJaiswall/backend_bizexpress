# Use a specific, compatible version of Python
FROM python:3.11.9-slim-bullseye

# Set the working directory
WORKDIR /app

# Install ffmpeg first
RUN apt-get update && apt-get install -y ffmpeg

# Copy requirements file
COPY requirements.txt .

# Install Python packages
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port and run the app
EXPOSE 10000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
