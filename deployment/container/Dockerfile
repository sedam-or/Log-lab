# syntax=docker/dockerfile:1
# Satu image untuk peran Source dan Monitor. Peran dan IP dipilih oleh command di compose.yaml,
# nilai env berasal dari config/*.example.env yang sama dengan VM (kontrak 1.1.0 tidak diubah).
# Base image dikunci dengan digest agar build dapat diulang.
FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src

# UID/GID 10001 sengaja tetap; direktori state dibuat di image agar volume baru mewarisi pemilik.
RUN groupadd --system --gid 10001 loglab \
    && useradd --system --uid 10001 --gid loglab --home-dir /nonexistent --no-create-home --shell /usr/sbin/nologin loglab \
    && install -d -o loglab -g loglab -m 0750 /var/lib/loglab /var/backups/loglab /run/loglab

WORKDIR /app

# Dependency dengan hash dari lock; --no-deps karena lock sudah memuat seluruh dependency transitif.
COPY requirements.lock ./
RUN pip install --require-hashes --no-deps -r requirements.lock

# contract.py membaca config/contract.json saat Settings dibuat (validasi env).
COPY config/contract.json ./config/contract.json
COPY src/ ./src/

USER 10001:10001
EXPOSE 8443
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["loglab.source_main:app", "--host", "172.16.202.21", "--port", "8443", "--ssl-certfile", "/etc/loglab/tls.crt", "--ssl-keyfile", "/etc/loglab/tls.key", "--no-access-log", "--no-server-header", "--log-level", "warning", "--timeout-graceful-shutdown", "5"]
