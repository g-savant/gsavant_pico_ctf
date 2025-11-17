FROM python:3.12-slim

# cmgr injects these per instance
ARG FLAG
ARG SECRET_SEED="default"

# System deps (psycopg/sqlite clients, wait-for scripts, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 && rm -rf /var/lib/apt/lists/*

# Flag + metadata
RUN install -d -m 0700 /challenge
COPY setup-challenge.py /challenge/setup-challenge.py
RUN python3 /challenge/setup-challenge.py

# App code
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app   

# e.g. gunicorn entry
EXPOSE 8080
# PUBLISH 8080 AS HTTP
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
