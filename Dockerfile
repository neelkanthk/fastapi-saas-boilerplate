# Use an official Python image as the base
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements file and install dependenciess at WORKDIR
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy the rest of your code into the container at WORKDIR
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]