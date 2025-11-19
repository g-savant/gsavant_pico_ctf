FROM python:3.12-slim


ARG FLAG="CTF"
ARG SEED="default"

ENV USER_DB_PATH="/tmp/web_inject.db" \
    FLAG_PATH="/challenge/flag" \
    ADMIN_PASS_PATH="/challenge/admin_password" \
    ADMIN_USERNAME="executive"

RUN install -d -m 0700 /challenge/
COPY setup-challenge.py /challenge/setup-challenge.py
RUN python3 /challenge/setup-challenge.py

WORKDIR /app
COPY ./main.py /app/main.py
COPY ./static /app/static
COPY requirements.txt .
RUN pip install -r requirements.txt


# Expose the port on which the Flask app will run
EXPOSE 8000

# PUBLISH 8000 AS HTTP
CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
