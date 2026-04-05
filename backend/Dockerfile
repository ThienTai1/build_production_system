# backend/Dockerfile
FROM python:3.11-slim

# Ngăn Python tạo file .pyc và bật stdout/stderr không qua buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cài đặt uv (Bộ quản lý thư viện siêu tốc)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy danh sách thư viện trước để tận dụng cache của Docker
COPY pyproject.toml uv.lock ./

# Cài đặt toàn bộ thư viện (frozen lockfile để đảm bảo đúng phiên bản)
RUN uv sync --frozen --no-dev

# Copy toàn bộ mã nguồn vào container
COPY app/ ./app/

# Port mà backend đang chạy
EXPOSE 8003

# Lệnh để khởi chạy (chạy qua uv để đảm bảo môi trường venv chuẩn)
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
