FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

COPY backend1/requirements.txt backend1/requirements.txt
RUN pip install --no-cache-dir -r backend1/requirements.txt

COPY . .

# Run as a non-root user; the SQLite file lives in /app/backend1 by default,
# so mount a volume there or set DATABASE_URL to use PostgreSQL.
RUN useradd --create-home app && chown -R app:app /app
USER app

EXPOSE 5000

# One worker: without SECRET_KEY / JWT_SECRET_KEY set, each process generates its own
# signing keys, so tokens would not validate across multiple workers.
CMD ["sh", "-c", "python backend1/init_db.py && exec gunicorn --workers 1 --bind 0.0.0.0:${PORT} run:app"]
