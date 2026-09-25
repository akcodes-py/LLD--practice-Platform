FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000

# Migrate, seed demo problems, then serve with gunicorn.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_problems && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health/')"
