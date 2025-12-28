FROM python:3.10.19-slim

WORKDIR /app

COPY services/summarizer_worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/summarizer_worker/src ./src

COPY libs ./libs

ENV PYTHONPATH=/app

CMD ["python", "-m", "src.main"]