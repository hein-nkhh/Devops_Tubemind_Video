# syntax=docker/dockerfile:1.4
# =========================
# Stage 1: Builder
# =========================
FROM python:3.10-slim AS builder

WORKDIR /app

# --- System deps (build) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# --- Copy requirements ---
COPY services/transcriber_worker/requirements.txt .

# --- Python deps ---
# Quan trọng:
# - NumPy < 2.0 (numba + whisper ổn định)
# - Torch CPU ONLY (ép index-url)
RUN pip install --upgrade pip \
 && pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt \
    --prefix=/install

# --- Copy source ---
COPY services/transcriber_worker/src ./src
COPY libs ./libs


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.10-slim

WORKDIR /app

# --- Runtime deps ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# --- Copy python packages ---
COPY --from=builder /install /usr/local

# --- Copy source ---
COPY --from=builder /app/src ./src
COPY --from=builder /app/libs ./libs

# --- Whisper cache ---
RUN mkdir -p /root/.cache/whisper

# --- ENV (CPU only, ổn định) ---
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV CUDA_VISIBLE_DEVICES=""
ENV WHISPER_FORCE_CPU=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1


CMD ["python", "-m", "src.main"]
