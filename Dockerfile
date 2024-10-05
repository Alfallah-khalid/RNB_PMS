# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Cloud Run will use
EXPOSE 8080

# Start the Flask app using gunicorn
CMD exec gunicorn --bind :$PORT main:app
