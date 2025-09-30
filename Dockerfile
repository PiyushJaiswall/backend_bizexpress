# Use an official Python image.
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port the app runs on
EXPOSE 10000

# Set the command to run your app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
