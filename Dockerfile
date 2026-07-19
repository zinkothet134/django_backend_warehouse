# 1. Use the official lightweight Python image
FROM python:3.11-slim

# 2. Set environment variables
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures Python output is logged to the terminal immediately for Seenode logs
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install system dependencies required for PostgreSQL
# I included postgresql-client so tools like pg_dump remain available 
# directly inside your production container if you ever need them.
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy the entire project into the container
COPY . .

# 7. Ensure your build script is executable
# Developing on a MacBook Air usually prevents Windows-style line-ending bugs, 
# but explicitly setting execution permissions here prevents the 'code 127' 
# execution errors when Seenode attempts to run it.
RUN chmod +x build.sh

# 8. Expose the port Django/Gunicorn will run on
EXPOSE 8000

# 9. Command to run the application using Gunicorn
# IMPORTANT: Replace 'your_project_name' with your actual main Django folder name
CMD ["gunicorn", "footwear_erp.wsgi.wsgi:application", "--bind", "0.0.0.0:8000"]