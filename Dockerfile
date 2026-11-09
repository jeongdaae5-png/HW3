FROM python:3.12.7-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY disk_analyzer.py disk_analyzerD.py requirements.txt README.md ./
RUN python --version && python -m pip --version \
    && python -m pip install --no-cache-dir --requirement requirements.txt \
    && python -m py_compile disk_analyzer.py disk_analyzerD.py
ENTRYPOINT ["python", "/app/disk_analyzerD.py"]
