# --- Stage 1: Build Stage ---
# Use an official Python image as a parent image
FROM python:3.11-slim as builder

# Set the working directory in the container
WORKDIR /usr/src/app

# Create and activate a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the requirements file into the container
COPY ./backend/requirements.txt ./

# Install project dependencies into the virtual environment
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final Stage ---
# Use a slim Python image for the final, smaller production image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the installed virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Add the virtual environment to the PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application source code and the models into the container
# These paths are now relative to the project root, which is our build context.
COPY ./backend/src/ /app/src
COPY ./models/ /app/models

# Set the PYTHONPATH to include the src directory
# This is crucial for the Python interpreter to find the 'connect4' package.
ENV PYTHONPATH=/app/src

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# Use gunicorn for a production-ready server.
# We use a single worker (-w 1) to ensure that the in-memory session
# dictionary is shared across all requests. For a larger-scale application,
# this would be replaced by a shared session store like Redis.
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "src.connect4.api.main:app"]
