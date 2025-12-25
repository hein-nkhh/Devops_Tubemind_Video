# syntax=docker/dockerfile:1.4
# =========================
# Stage 1: Build stage
# =========================
FROM python:3.10-slim AS builder

WORKDIR /app

# --- System packages cho build ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# --- Copy requirements (bỏ torch) ---
COPY services/transcriber_worker/requirements.txt .

# --- Cài torch CPU riêng, không GPU ---
RUN pip install --no-cache-dir \
    torch==2.9.1 \
    torchvision==0.16.0 \
    torchaudio==2.0.2 \
    --prefix=/install

# --- Cài các package còn lại (Whisper không include model) ---
RUN pip install --no-cache-dir -r requirements.txt --prefix=/install

# --- Copy source ---
COPY services/transcriber_worker/src ./src
COPY libs ./libs

# =========================
# Stage 2: Final lightweight image
# =========================
FROM python:3.10-slim

WORKDIR /app

# --- System packages runtime ---
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# --- Copy Python packages từ builder ---
COPY --from=builder /install /usr/local

# --- Copy source ---
COPY --from=builder /app/src ./src
COPY --from=builder /app/libs ./libs

# --- Whisper cache (model download lúc run) ---
RUN mkdir -p /root/.cache/whisper

# --- Env ---
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV CUDA_VISIBLE_DEVICES=""

CMD ["python", "src/main.py"]
