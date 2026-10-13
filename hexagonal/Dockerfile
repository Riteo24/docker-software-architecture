FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt requirements-dev.txt ./
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt \
    && pip wheel --no-cache-dir --wheel-dir /test-wheels -r requirements-dev.txt

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8081
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home app
COPY --chown=app:app . .
    RUN mkdir -p /data && chown app:app /data
USER app
EXPOSE 8081
HEALTHCHECK --interval=10s --timeout=4s --start-period=40s --retries=5 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8080')+'/health', timeout=3)"
CMD ["python", "-m", "config.start"]

FROM runtime AS test
USER root
COPY --from=builder /test-wheels /test-wheels
RUN pip install --no-cache-dir --no-index --find-links=/test-wheels /test-wheels/* && rm -rf /test-wheels
USER app
CMD ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]

FROM runtime AS production
