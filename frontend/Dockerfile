# Use an official Python image as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the frontend directory
COPY frontend/requirements.txt ./

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application code from the frontend directory
COPY frontend/app.py ./

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit application
# The --server.enableCORS=false flag is important for when this is behind a reverse proxy
# The --server.address=0.0.0.0 makes it accessible from outside the container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false"]

