FROM python:3.10.19-slim

WORKDIR /app

COPY services/notifier_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/notifier_service/src ./src

COPY libs ./libs

ENV PYTHONPATH=/app

CMD ["python", "-m", "src.main"]