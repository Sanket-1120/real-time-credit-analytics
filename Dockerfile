# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container
COPY . .

# Tell Docker that the container will listen on port 10000
EXPOSE 10000

# The command to run your application when the container starts
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]