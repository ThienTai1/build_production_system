# 🐳 Docker Infrastructure Architecture

Hệ thống Senior AI Agent của bạn được hỗ trợ bởi một loạt các dịch vụ chạy nền (background services) được quản lý chung qua tệp `docker-compose.yaml`. Việc đóng gói các dịch vụ này vào Docker giúp tách biệt môi trường cài đặt phức tạp ra khỏi mã nguồn chính của Python và Next.js.

Dưới đây là sơ đồ và giải thích chi tiết cho từng dịch vụ đang chạy:

> [!TIP]
> Tất cả các dịch vụ này đều được chia sẻ chung một mạng nội bộ tên là `monitoring`, cho phép chúng dễ dàng "nhìn thấy" và nói chuyện với nhau thông qua tên container (VD: Prometheus có thể gọi trực tiếp tới `loki:3100`).

---

## 💾 Core Vector Database (Lưu trữ Trí nhớ AI)

### 1. `milvus` (Vector Database)
*   **Nhiệm vụ:** Đây là "bộ não dài hạn" của AI. Nó lưu trữ các vector đa chiều (embeddings) của tài liệu và cho phép tìm kiếm ngữ nghĩa cực nhanh (Tìm câu trả lời liên quan nhất tới câu hỏi).
*   **Port:** `19530`
*   **Lưu ý:** Chúng ta sử dụng `platform: linux/amd64` để đảm bảo nó chạy ổn định trên chip Apple Silicon (Mac M4) của bạn thông qua trình giả lập rosetta.

### 2. `etcd` (Metadata Storage)
*   **Nhiệm vụ:** Đây là dịch vụ "trợ lý" bắt buộc của Milvus. Nó lưu trữ các thông tin cấu trúc (metadata) như danh sách các collection, phân quyền, cấu trúc dữ liệu của Milvus. Milvus không thể hoạt động nếu không có etcd.

### 3. `minio` (Object Storage)
*   **Nhiệm vụ:** Đây là một dịch vụ giống hệt Amazon S3 nhưng chạy ở máy bạn (Local S3). Nó là dịch vụ bắt buộc thứ 2 của Milvus. Milvus dùng MinIO để lưu trữ các file dữ liệu log thô (raw data files) và các tệp chỉ mục khổng lồ mà không tiện nhét vào RAM.

---

## 📈 Giám sát & Đo lường (Metrics)

### 4. `prometheus` (Metrics Database)
*   **Nhiệm vụ:** Định kỳ (khoảng 5-10s một lần), Prometheus sẽ quét qua địa chỉ `/metrics` của ứng dụng Backend để "hút" các dữ liệu như: Tổng số câu hỏi đã hỏi, thời gian delay, số lượng lỗi.
*   **Cơ chế:** Lưu trữ dữ liệu dạng Time-series (Chuỗi thời gian) để bạn có thể xem lại lịch sử hệ thống trong quá khứ.

---

## 📝 Nhật ký & Dấu vết (Logs & Traces)

### 5. `loki` (Log Aggregation)
*   **Nhiệm vụ:** Máy chủ thu thập toàn bộ các bản ghi sự kiện (Logging) của hệ thống. Nó được thiết kế bởi hãng Grafana nên tốc độ tìm kiếm log cực kỳ nhanh.

### 6. `tempo` (Distributed Tracing)
*   **Nhiệm vụ:** Lưu trữ các "Trace". Một trace là một chuyến đi (journey). Ví dụ: Khi bạn hỏi 1 câu, Tempo sẽ ghi nhận bước 1: Lấy tài liệu tốn 0.5s; Bước 2: Gọi Ollama tốn 10s. Bạn sẽ biết đích xác mình đang bị chậm ở đâu.

### 7. `otel-collector` (OpenTelemetry Collector)
*   **Nhiệm vụ:** Một "tổng đài trung chuyển". Thay vì app Python phải tự đi gửi dữ liệu rải rác đến Loki và Tempo, Python chỉ việc ném cục dữ liệu đó cho OTel Collector. Collector sẽ chịu trách nhiệm phân loại và gửi Traces vào Tempo, gửi Logs vào Loki.

---

## 🧠 Theo dõi AI Chuyên sâu

### 8. `langfuse` & `langfuse-db` (LLM Observability)
*   **Nhiệm vụ:** Mặc dù Tempo/Loki rất tốt, nhưng chúng chỉ dùng cho giới IT (Server chạy mất mấy giây). **Langfuse** là nền tảng dành riêng cho AI. Nó cho bạn đọc trực tiếp **Prompt** mà hệ thống đã lắp ghép, xem câu trả lời thô của AI, đo lường số Token đã dùng và đánh giá chất lượng câu trả lời.
*   **DB:** Langfuse chạy trên một cơ sở dữ liệu `postgres` riêng biệt vì nó cần lưu trữ rất nhiều metadata của các phiên chat.
*   **Port:** `3002`

---

## 📊 Bảng Điều Khiển (Dashboard)

### 9. `grafana` (Visualization Hub)
*   **Nhiệm vụ:** Giao diện đẹp mắt kết nối với Prometheus (Metrics), Loki (Logs), và Tempo (Traces). Grafana tổng hợp tất cả thành các biểu đồ và dashboard chuyên nghiệp, giúp bạn theo dõi "sức khỏe" của toàn hệ thống tại một nơi duy nhất.
*   **Port:** `3000`
