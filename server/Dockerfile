FROM python:3.14-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN mkdir -p /data/knowledge

ENV DATABASE_URL=sqlite:////data/knowledge/knowledge.db
ENV FILE_STORAGE_ROOT=/data/knowledge/storage
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
