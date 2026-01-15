# Use a lightweight Python 3.10 image
FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for PDF and Docx processing
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Ensure the upload directory exists
RUN mkdir -p uploads/resumes

# Expose the FastAPI port
EXPOSE 8000

# Run the application using uvicorn
CMD ["uvicorn", "app.core.main:app", "--host", "0.0.0.0", "--port", "8000"]