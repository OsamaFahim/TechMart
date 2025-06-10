FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for mysqlclient and netcat
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev pkg-config netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy everything from backend/ (including manage.py, Techmart/, etc.)
COPY . .

# Make sure wait-for-it.sh is executable
RUN chmod +x /app/Techmart/wait-for-it.sh && chmod +x /app/Techmart/entrypoint.sh

# Collect static files
RUN python Techmart/manage.py collectstatic --noinput

EXPOSE 8000

CMD ["./Techmart/entrypoint.sh"]