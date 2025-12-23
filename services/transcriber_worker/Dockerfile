FROM python:3.11-slim

WORKDIR /app

# copy requirements từ root
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy source code của service
COPY services/transcriber_worker/src ./src

CMD ["python", "-m", "src.main"]
