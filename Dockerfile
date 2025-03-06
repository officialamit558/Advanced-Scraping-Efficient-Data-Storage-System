# Use Python 3.12 slim as base image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose Flask's default port
EXPOSE 5000

# Set the correct command to run Flask app
CMD ["python", "dashboard/app.py"]
