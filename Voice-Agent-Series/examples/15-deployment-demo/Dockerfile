FROM python:3.12-slim
WORKDIR /app
COPY --chown=10001:10001 health_demo.py /app/health_demo.py
USER 10001:10001
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HEALTH_HOST=0.0.0.0 HEALTH_PORT=8105
EXPOSE 8105
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8105/health/ready',timeout=2).read()"
CMD ["python", "health_demo.py"]
