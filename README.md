# Devops_Tubemind_Video


Devops_Tubemind_Video-AI/
├── .gitignore               # Ignore venv, .env, __pycache__, .terraform
├── .dockerignore            # Global ignore cho Docker context
├── README.md                # Documentation tổng quan dự án
├── Makefile                 # Các lệnh shortcut (setup, test, build, deploy)
├── docker-compose.dev.yml   # Môi trường Local (Postgres, Redis, MinIO)
│
├── ..jenkins # Chứa template cho PR/Issue
│
├── libs/                    # SHARED LIBRARY (Cực quan trọng để Consistency)
│   └── common/              # Code dùng chung cho cả 4 services
│       ├── __init__.py
│       ├── logger.py        # Cấu hình logging chuẩn JSON (cho ELK đọc)
│       ├── redis_client.py  # Wrapper kết nối Redis (retry logic)
│       ├── constants.py     # Tên Queue, Status Enum (PENDING, DONE)
│       └── utils.py         # Hàm validate URL, clean string...
│
├── services/                # SOURCE CODE CÁC MICROSERVICES
│   │
│   ├── api-gateway/         # Service 1: Cổng vào (FastAPI)
│   │   ├── src/
│   │   │   ├── api/         # Chứa Routes (Endpoints)
│   │   │   │   └── v1/      # Versioning API
│   │   │   │       ├── auth.py
│   │   │   │       └── video.py
│   │   │   ├── core/        # Config load từ Env
│   │   │   │   ├── config.py
│   │   │   │   └── security.py
│   │   │   ├── schemas/     # Pydantic Models (Request/Response DTO)
│   │   │   │   └── video_dto.py
│   │   │   ├── services/    # Business Logic (Gọi Queue, check DB)
│   │   │   │   └── producer.py
│   │   │   └── main.py      # Entry point
│   │   ├── tests/           # Unit test cho Gateway
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── sonar-project.properties # Config riêng cho từng service
│   │
│   ├── transcriber-worker/  # Service 2: AI Transcribe (Python)
│   │   ├── src/
│   │   │   ├── core/        # Config AI Model (Whisper size...)
│   │   │   ├── workers/     # Logic lắng nghe Queue
│   │   │   │   └── consumer.py
│   │   │   ├── ai_engine/   # Code xử lý Whisper
│   │   │   │   └── whisper_handler.py
│   │   │   └── main.py
│   │   ├── Dockerfile       # Lưu ý: Cài ffmpeg, driver âm thanh
│   │   └── requirements.txt
│   │
│   ├── summarizer-worker/   # Service 3: AI Summarize (Python)
│   │   ├── src/
│   │   │   ├── prompts/     # Chứa template prompt cho LLM
│   │   │   │   └── summary_prompt.txt
│   │   │   ├── llm_engine/  # Code gọi LangChain/OpenAI/Llama
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── notifier-service/    # Service 4: Gửi thông báo
│       ├── src/
│       │   ├── adapters/    # Code kết nối AWS SNS / Email
│       │   └── main.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── infra/                   # INFRASTRUCTURE AS CODE (Ops Team)
│   │
│   ├── terraform/           # Dựng hạ tầng AWS
│   │   ├── environments/    # Tách biệt môi trường
│   │   │   ├── dev/
│   │   │   │   ├── main.tf
│   │   │   │   └── terraform.tfvars
│   │   │   └── prod/
│   │   ├── modules/         # Các module tái sử dụng
│   │   │   ├── vpc/
│   │   │   ├── eks/
│   │   │   ├── rds/
│   │   │   └── elasticache/
│   │
│   ├── k8s/                 # Kubernetes Manifests & Helm
│   │   ├── helm-charts/     # Helm Chart tự viết
│   │   │   └── tubemind-app/ # Generic chart dùng cho cả 4 services
│   │   │       ├── templates/
│   │   │       ├── Chart.yaml
│   │   │       └── values.yaml
│   │   ├── argocd/          # Config cho ArgoCD Application
│   │   │   ├── dev-app.yaml
│   │   │   └── prod-app.yaml
│   │   └── monitoring/      # Config Prometheus/Grafana
│
└── ci-cd/                   # PIPELINE SCRIPTS
    ├── jenkins/
    │   ├── Jenkinsfile.build  # Build & Push Image
    │   └── Jenkinsfile.deploy # Trigger ArgoCD sync (optional)
    ├── scripts/
    │   ├── run-sonar.sh       # Script chạy Sonar scanner
    │   └── run-trivy.sh       # Script chạy Trivy scan
    └── sonar-project.properties # Global config (nếu quét cả repo)