
FROM python:3.10.19-slim

WORKDIR /app

COPY services/summarizer-worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/summarizer-worker/src ./src

COPY libs ./libs

ENV PYTHONPATH=/app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]