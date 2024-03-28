# Use an official Python runtime as a parent image
FROM python:3.9.7

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run gunicorn server when the container launches
CMD ["gunicorn", "-w", "1", "-k", "eventlet", "--bind", "0.0.0.0:3000", "--log-level","debug","server:app"]