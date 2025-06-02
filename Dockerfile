FROM python:3.13-alpine AS builder

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-alpine

RUN adduser -D -u 1000 appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

COPY ttc_alerts/ ./ttc_alerts/

USER appuser

ENV PYTHONPATH=/app

CMD ["python3", "-m", "ttc_alerts.views.cli", "--monitor"]
