# Danh Sách Thành Viên & Báo Cáo Phân Công Nhóm

- **Tên Nhóm:** `Beta`
- **Mã Nhóm / Lớp:** `K4-L3B-DAY10`
- **Tên Repository Nộp Bài:** `K4-L3B-DAY10-Beta-DataPipelineDataObservability`

---

## # Thành viên

| STT | Họ và tên | MSSV | Email | Vai trò & Phân công công việc | Báo cáo cá nhân |
|---:|---|---|---|---|---|
| 1 | Đinh Kim Thái | 2A202602417 | kimthaik17@gmail.com | **Data Engineer / Data Observability Engineer / DevOps**<br>- Raw Data Ingestion & Lineage (`crossref.py`)<br>- Data Cleaning & Pre-embed Modeling (`cleaning.py`)<br>- Data Quality Gate (GX 1.x) & Freshness SLA (`quality.py`)<br>- Data Corruption Suite & Repair Logic (`corruption.py`)<br>- **Bonus B1:** Observability Streamlit Dashboard (`app.py`)<br>- **Bonus B3:** Pytest CI Test Suite & GitHub Actions (`tests/*`, `.github/workflows/ci.yml`) | `report/2A202602417_DinhKimThai.md` |
| 2 | Nguyễn Lê Phước Tiến | 2A202602616 | nlptien1809@gmail.com | **RAG / Evaluation Engineer**<br>- Evaluation Dataset Benchmark (`testset.py`)<br>- Embedding & ChromaDB Vector Store (`retrieval/*`)<br>- Multi-provider QA Agent (`agent.py`, `qa.py`)<br>- Pipeline Orchestration & Metrics (`phase1.py`, `corruption_flow.py`)<br>- Báo cáo nhóm & Tích hợp (`report/group_report.md`, `data/reports/*`) | `report/2A202602616_NguyenLePhuocTien.md` |

---

## # Cá nhân

### ## DinhKimThai-2A202602417
- **Vai trò:** Data Engineer / Data Observability Engineer / DevOps.
- **Main Files:** `src/ingestion/crossref.py`, `src/ingestion/cleaning.py`, `src/observability/quality.py`, `src/ingestion/corruption.py`, `app.py`, `tests/*`, `.github/workflows/ci.yml`, `pyproject.toml`.
- **Main Artifacts:** `data/raw/*`, `data/clean/*`, `data/quality/*`, `data/results/corruption_log.json`, `app.py`, `.github/workflows/ci.yml`, `tests/*`.
- **Công việc chi tiết đã hoàn thành:**
  - **Raw Ingestion & Lineage:** Xây dựng module thu thập Crossref API với cơ chế Fallback offline trong `src/ingestion/crossref.py`, xuất bản sao lưu `crossref_response.json` và `crossref_records.json`.
  - **Data Cleaning & Modeling:** Khử trùng lặp theo `paper_id`, tính toán trường `age_days` chuẩn timezone UTC và tạo trường `text_for_embedding` (cấu trúc 5 phần) trong `src/ingestion/cleaning.py`, xuất `papers_clean.csv` và `papers_clean.json`.
  - **Data Quality Gate:** Thiết lập chốt kiểm dịch chất lượng tự động theo chuẩn mới **Great Expectations 1.x** (Ephemeral Context, 4 nhóm Expectations thiết yếu) và giám sát Freshness SLA trong `src/observability/quality.py`, xuất `baseline_quality_report.json` và `freshness_report.json`.
  - **Data Corruption & Repair:** Xây dựng 6 kịch bản tiêm lỗi dữ liệu giả lập sự cố trong `src/ingestion/corruption.py`, xuất `corruption_log.json`, và thiết kế cơ chế Idempotent Repair khôi phục từ raw snapshot.
  - **Observability Web Dashboard (Bonus B1):** Phát triển giao diện Web Dashboard tương tác thời gian thực (`app.py`) bằng Streamlit & Plotly trực quan hóa tình trạng Data Quality Gate, Freshness SLA, so sánh 3 trạng thái Baseline/Corrupted/Repaired và công cụ Vector Search thử nghiệm.
  - **Pytest CI Suite & Automated Testing (Bonus B3):** Xây dựng bộ unit test kiểm thử toàn diện 4 module chính (`tests/test_ingestion.py`, `test_cleaning.py`, `test_quality.py`, `test_corruption.py`) đạt 100% pass rate, cấu hình `pyproject.toml` và tự động hóa qua GitHub Actions CI (`.github/workflows/ci.yml`).
- **Điều học được / Đóng góp chính:**
  - Nắm vững kỹ thuật truy vết nguồn gốc dữ liệu (Data Lineage), cơ chế phát hiện và ngăn chặn lỗi ngầm (Silent Failure) trước khi dữ liệu được nạp vào Vector Database, cùng kỹ năng đóng gói ứng dụng Observability Dashboard & triển khai CI/CD pipeline tự động.

---

### ## NguyenLePhuocTien-2A202602616
- **Vai trò:** RAG / Evaluation Engineer.
- **Main Files:** `src/evaluation/testset.py`, `src/retrieval/*` (`index.py`, `embeddings.py`, `agent.py`, `qa.py`), `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`, `script/*`, `report/*`.
- **Main Artifacts:** `data/eval/*`, `data/chroma/*`, `data/results/baseline_metrics.json`, `data/results/corrupted_metrics.json`, `data/results/repaired_metrics.json`, `data/reports/*`.
- **Công việc chi tiết đảm nhiệm:**
  - **Evaluation Benchmark:** Xây dựng bộ câu hỏi kiểm thử trong `src/evaluation/testset.py` phủ đủ 4 nhóm nghiệp vụ (`summary`, `authors`, `date`, `categories`), lưu tại `data/eval/test_set.json`.
  - **Embedding & Vector Store:** Quản lý mô hình `sentence-transformers/all-MiniLM-L6-v2`, nạp vector vào 3 collection ChromaDB tách biệt (`papers-baseline`, `papers-corrupted`, `papers-repaired`) trong `src/retrieval/index.py`.
  - **QA Agent Retrieval:** Xây dựng router và prompt template trích xuất câu trả lời chuẩn xác từ ngữ cảnh tài liệu (`src/retrieval/qa.py`, `agent.py`).
  - **Pipeline Orchestration & Scoring:** Kết nối luồng chạy end-to-end trong `src/pipelines/phase1.py` và `src/pipelines/corruption_flow.py`, đo lường chỉ số Retrieval Hit Rate và Token F1 trên 3 trạng thái Baseline, Corrupted và Repaired.
  - **Reporting:** Xuất báo cáo Pha 1 (`phase1_report.md`), báo cáo đối chiếu 3 trạng thái (`corruption_report.md`) và chủ trì hoàn thiện báo cáo nhóm `report/group_report.md`.
- **Điều học được / Đóng góp chính:**
  - Hiểu sâu sắc về thiết kế hệ thống RAG Agent thực tế, phương pháp đo lường định lượng sự suy giảm hiệu năng khi dữ liệu bị lỗi và chứng minh năng lực phục hồi của hệ thống.
