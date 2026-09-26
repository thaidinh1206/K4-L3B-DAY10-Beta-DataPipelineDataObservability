# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin | Nội dung |
| ------------------ | -------------------------- |
| Khóa/Lớp | K4 - L3B (Ca Sáng) |
| Tên nhóm | Beta |
| Repository | https://github.com/thaidinh1206/K4-L3B-DAY10-Beta-DataPipelineDataObservability |
| Ngày hoàn thành | 2026-09-26 |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Đinh Kim Thái | 2A202602417 | Data Engineer / Data Observability Engineer | `src/ingestion/*`, `src/observability/quality.py`, `data/raw/*`, `data/clean/*`, `data/quality/*`, `corruption_log.json` |
| 2 | Nguyễn Lê Phước Tiến | 2A202602616 | RAG / Evaluation Engineer | `src/evaluation/*`, `src/retrieval/*`, `src/pipelines/*`, `script/*`, `data/eval/*`, `data/chroma/*`, `*_metrics.json`, `data/reports/*` |

---

## 2. Tóm tắt kết quả

Nhóm Beta đã hoàn thành trọn vẹn end-to-end Data Pipeline và hệ thống Data Observability cho RAG Agent qua 6 mốc Checkpoint (CP0 – CP5). 

Ở pha Baseline, pipeline thu thập thành công 24 bản ghi metadata nghiên cứu từ Crossref API, chuẩn hóa văn bản, tính toán `age_days` và ghép cấu trúc `text_for_embedding` 5 phần. Chốt kiểm dịch chất lượng tự động **Great Expectations 1.x** đánh giá đạt `success=True` (7/7 Expectations passed) và giám sát Freshness SLA xác nhận `is_fresh=True` (tỷ lệ quá hạn 4.17% <= 25%). Trên dữ liệu sạch, RAG Agent đạt **Retrieval Hit Rate = 100%**, **Mean Token F1 = 68.8%** và **Judge Accuracy = 80%**.

Khi thực thi **Synthetic Data Corruption** với 6 kịch bản tiêm lỗi, hệ thống minh chứng hiện tượng **Silent Failure**: RAG Agent tiếp tục phục vụ truy vấn mà không phát sinh exception, nhưng chỉ số Hit Rate sụt giảm nghiêm trọng xuống **80%** (giảm 20%), Token F1 giảm xuống **61.1%** và Judge Accuracy giảm xuống **60%**. Chốt kiểm định GX 1.x đã phát hiện bất thường và báo **FAIL** chính xác.

Cuối cùng, cơ chế **Idempotent Repair** tự động tái cấu trúc dữ liệu sạch từ Raw Snapshot bất biến ban đầu, đưa toàn bộ chỉ số chất lượng dữ liệu (Quality Gate PASS, Freshness PASS) và chỉ số hiệu năng RAG (Hit Rate 100%, Token F1 68.8%) phục hồi trọn vẹn 100% trở lại mức Baseline.

---

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref API / Snapshot (data/raw/crossref_response.json)
    └──> Raw Records (data/raw/crossref_records.json)
            └──> Data Cleaning & Modeling (text_for_embedding, age_days)
                    └──> Quality & Freshness Reports (data/quality/)
                    └──> Embedding (all-MiniLM-L6-v2) + ChromaDB Index (data/chroma/)
                    └──> Evaluation Baseline (10 câu benchmark) ──> baseline_metrics.json
                            │
                            ├──> Data Corruption (6 kịch bản) ──> Re-index & Re-eval ──> corrupted_metrics.json
                            │
                            └──> Idempotent Repair (từ Raw) ──> Re-index & Re-eval ──> repaired_metrics.json
                                    └──> Báo cáo đối chiếu 3 trạng thái (corruption_report.md)
```

### Trách nhiệm của từng khối

| Khối | Input | Xử lý chính | Output/artifact | Owner |
| ----------------- | -------------- | -------------------------- | ------------------------ | -------------- |
| **Ingestion** | Crossref API / Snapshot | Fetch, retry, parse JATS XML tag, lưu raw artifacts | `data/raw/crossref_response.json`<br>`data/raw/crossref_records.json` | Đinh Kim Thái |
| **Cleaning** | 24 `PaperRecord` | Khử trùng `paper_id`, tính `age_days`, tạo `text_for_embedding` | `data/clean/papers_clean.csv`<br>`data/clean/papers_clean.json` | Đinh Kim Thái |
| **Embedding/index** | Clean DataFrame | Sinh vector `all-MiniLM-L6-v2`, nạp ChromaDB collections | `data/chroma/`<br>`data/embeddings/` | Nguyễn Lê Phước Tiến |
| **Evaluation** | Clean DataFrame & Vector DB | Sinh 10 câu test benchmark, tính Hit Rate, Token F1, LLM Judge | `data/eval/test_set.json`<br>`data/results/*_metrics.json` | Nguyễn Lê Phước Tiến |
| **Observability** | DataFrame sạch/bẩn | Kiếm định Great Expectations 1.x & giám sát Freshness SLA | `data/quality/baseline_quality_report.json`<br>`data/quality/freshness_report.json` | Đinh Kim Thái |
| **Corruption/repair** | Clean DataFrame & Raw Snapshot | Tiêm 6 kịch bản lỗi, khôi phục idempotent từ Raw snapshot | `data/results/corruption_log.json`<br>`data/reports/corruption_report.md` | Đinh Kim Thái & Nguyễn Lê Phước Tiến |
| **Orchestration** | Config & Modules | Điều phối luồng Phase 1 và Corruption Flow end-to-end | `script/run_phase1.py`<br>`script/run_corruption_flow.py` | Nguyễn Lê Phước Tiến |

---

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình | Giá trị sử dụng |
| ---------------------------- | ------------------- |
| `LLM_PROVIDER` | `gemini` (hoặc `mock`) |
| `LLM_MODEL` | `gemini-2.5-flash` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Số lượng Crossref records | `24` |
| Retrieval `top_k` | `4` |
| Freshness threshold | `180` ngày |
| Random seed | `42` |

### Lệnh cài đặt

```bash
python -m pip install -e .
```

### Lệnh chạy

**Baseline Pipeline (Pha 1):**
```bash
python script/run_phase1.py
```

**Corruption & Repair Flow (Pha 2):**
```bash
python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh | Trạng thái | Thời điểm chạy gần nhất | Bằng chứng |
| ----------------- | ----------------------------------------------- | ----------------------------- | ------------------------------------ |
| **Baseline pipeline** | Thành công | 2026-09-26 11:30 | `baseline_metrics.json`, `phase1_report.md` |
| **Corruption flow** | Thành công | 2026-09-26 11:45 | `corrupted_metrics.json`, `repaired_metrics.json`, `corruption_report.md` |

---

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính | Giá trị |
| --------------------------- | ------------------------------------- |
| Source | Crossref REST API (`https://api.crossref.org/works`) / Offline Snapshot |
| Query/filter | `agentic retrieval augmented generation large language model` |
| Thời điểm lấy dữ liệu | 2026-09-26 |
| Số record nhận được | 24 |
| Cơ chế retry/backoff | Retry 3 lần khi 429/503, tự động fallback đọc snapshot local `crossref_response.json` |

### Raw và clean schema

| Trường | Kiểu dữ liệu | Bắt buộc? | Ý nghĩa | Xử lý khi thiếu/sai |
| --------------- | --------------- | ------------ | ----------- | ---------------------- |
| `paper_id` | String (DOI) | Có | Mã định danh duy nhất bài báo | Bỏ qua dòng nếu thiếu |
| `title` | String | Có | Tiêu đề bài báo | Bóc sạch JATS XML tag |
| `summary` | String | Có | Tóm tắt (Abstract) | Bóc sạch XML tag; gán rỗng nếu không có |
| `authors` | List[String] | Có | Danh sách tác giả | Gán `["Unknown"]` nếu thiếu |
| `categories` | List[String] | Có | Chủ đề nghiên cứu | Gán `["General"]` nếu thiếu |
| `published` | String (YYYY-MM-DD) | Có | Ngày xuất bản | Fallback về ngày `created` hoặc `2026-01-01` |
| `age_days` | Integer | Có | Độ tuổi tính theo ngày | `(run_date - published).days` |
| `text_for_embedding` | String | Có | Văn bản phục vụ AI embedding | Ghép chuẩn 5 phần |

### Quy tắc cleaning

| Quy tắc | Quality dimension liên quan | Số record bị tác động | Cách xác minh |
| ---------------------------------------- | ---------------------------- | -------------------------: | -------------------- |
| Loại bỏ thẻ JATS XML (`<jats:p>`) | Validity / Accuracy | 24 | Regex clean trong `cleaning.py` |
| Deduplicate theo `paper_id` | Uniqueness | 0 (Dữ liệu gốc đủ 24 bài độc nhất) | `drop_duplicates(subset=["paper_id"])` |
| Tính toán `age_days` chuẩn UTC | Timeliness / Freshness | 24 | Timestamp subtraction |

**Cách tạo `text_for_embedding`:**
```text
Title: <title>
Authors: <authors_joined>
Published: <published>
Abstract: <summary>
Categories: <categories_joined>
```

---

## 6. Evaluation setup

| Thành phần | Cấu hình thực tế |
| ---------------------------------------- | ----------------------------- |
| Số câu hỏi | `10` câu benchmark |
| Các `question_type` | `summary`, `authors`, `date`, `categories` |
| Ground-truth document ID | Trích xuất trực tiếp `paper_id` của bài báo chứa đáp án |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector store / collection | ChromaDB (`papers-baseline`, `papers-corrupted`, `papers-repaired`) |
| Retrieval `top_k` | `4` |
| LLM provider / model | Gemini (`gemini-2.5-flash`) hoặc Mock provider |
| Test set dùng chung cho 3 trạng thái | `data/eval/test_set.json` |

**Giải thích vì sao giữ nguyên test set:**  
Việc dùng chung một tập 10 câu hỏi benchmark cho cả 3 trạng thái (Baseline, Corrupted, Repaired) đảm bảo tính khoa học và biến số kiểm soát (Controlled Experiment). Sự thay đổi của các chỉ số `retrieval_hit_rate` hay `token_f1` hoàn toàn phản ánh biến động của chất lượng dữ liệu chứ không bị ảnh hưởng bởi độ khó ngẫu nhiên của câu hỏi.

---

## 7. Kết quả baseline

### Artifact checklist

| Artifact | Đường dẫn thực tế | Trạng thái | Ghi chú |
| ------------------------ | -------------------------------------- | ------------ | ---------- |
| Raw response/records | `data/raw/` | Có | `crossref_response.json`, `crossref_records.json` |
| Cleaned dataset | `data/clean/` | Có | `papers_clean.csv`, `papers_clean.json` |
| Embedding manifest/index | `data/embeddings/`, `data/chroma/` | Có | ChromaDB collectionsPersisted |
| Evaluation set | `data/eval/` | Có | `test_set.json` (10 câu benchmark) |
| Baseline metrics | `data/results/baseline_metrics.json` | Có | Hit Rate = 1.0, Token F1 = 0.6876 |
| Quality/freshness | `data/quality/` | Có | `baseline_quality_report.json`, `freshness_report.json` |
| Baseline report | `data/reports/phase1_report.md` | Có | Xuất báo cáo pha 1 hoàn chỉnh |

### Baseline metrics

| Metric | Giá trị | Diễn giải |
| ---------------------- | --------------: | --------------------------------------- |
| `retrieval_hit_rate` | **1.0 (100.0%)** | Top 4 kết quả truy vấn luôn chứa bài báo gốc chuẩn |
| `mean_token_f1` | **0.6876 (68.8%)** | Độ trùng khớp từ vựng cao giữa đáp án sinh ra và đáp án chuẩn |
| `judge_accuracy` | **0.8 (80.0%)** | LLM Judge đánh giá 8/10 câu đạt yêu cầu chính xác |
| `mean_judge_score` | **3.6 / 5.0** | Điểm trung bình chất lượng câu trả lời |

---

## 8. Data quality và freshness

### Quality checks (Great Expectations 1.x)

| Check | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline | Bằng chứng |
| ------------ | ----------------- | ------------------ | ----------------------- | ------------ |
| `ExpectTableRowCountToBeBetween` | Completeness | [10, 100] dòng | PASS (24 dòng) | `baseline_quality_report.json` |
| `ExpectColumnValuesToNotBeNull` | Completeness | `paper_id`, `title`, `text_for_embedding` not null | PASS (0 null) | `baseline_quality_report.json` |
| `ExpectColumnValuesToBeUnique` | Uniqueness | `paper_id` unique | PASS (0 duplicate) | `baseline_quality_report.json` |
| `ExpectColumnValueLengthsToBeBetween` | Validity | `title` [8, 500], `summary` [20, 5000] | PASS | `baseline_quality_report.json` |

### Freshness

| Thuộc tính | Giá trị |
| -------------------------- | ----------------------------------- |
| Freshness được đo tại | Cleaned Dataset (`papers_clean.json`) |
| Timestamp mới nhất | `2026-07-22` |
| Timestamp cũ nhất | `2026-03-28` |
| Ngưỡng freshness | `180` ngày |
| Trạng thái baseline | **Fresh (`is_fresh = True`)** |
| Lý do | Chỉ có 1/24 bài báo cũ hơn 180 ngày (~4.17% <= 25% ngưỡng SLA) |

---

## 9. Corruption scenarios và repair

| Corruption | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế | Cách repair |
| ------------------ | ---------- | ---------------------: | ------------------------ | --------------------- | -------------- |
| `drop_latest_records` | Xóa 20% bài mới nhất | 5 bài | Row count sụt giảm | Retrieval Hit Rate giảm 20% | Nạp lại từ Raw snapshot |
| `blank_summary` | Gán rỗng abstract | 2 bài | GX summary length FAIL | LLM thiếu context, Token F1 giảm | Khôi phục abstract từ Raw snapshot |
| `inject_noise` | Chèn chuỗi rác | 2 bài | Vector distance bị méo | Token F1 và Judge Accuracy giảm | Làm sạch chuỗi rác từ Raw snapshot |
| `truncate_title` | Cắt tiêu đề < 8 chars | 2 bài | GX title length FAIL | Nhận diện tiêu đề kém | Khôi phục title gốc từ Raw snapshot |
| `stale_date` | Lùi ngày về 2022 | 8 bài | Freshness SLA `is_fresh=False` | Tỷ lệ stale > 25% | Khôi phục ngày gốc từ Raw snapshot |
| `duplicate_rows` | Nhân bản 2 dòng | 2 bài | GX paper_id unique FAIL | Kết quả truy vấn bị trùng lặp | Khử trùng lặp theo `paper_id` |

**Corruption log:** `data/results/corruption_log.json` (Trạng thái: Có, ghi nhận đủ 6 kịch bản).

**Cơ chế Repair đảm bảo tính Idempotent:**  
Hệ thống không vá lỗi thủ công trên file bẩn mà đọc lại 100% bản lưu trữ thô bất biến ban đầu (`data/raw/crossref_records.json`) và thực thi lại pipeline làm sạch. Điều này đảm bảo tính an toàn, tính tái lập và phục hồi trọn vẹn dữ liệu gốc.

---

## 10. So sánh baseline, corrupted và repaired

| Metric/signal | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi | Nhận xét |
| ------------------------ | -------: | --------: | -------: | -----------------------: | --------------: | ------------ |
| `retrieval_hit_rate` | **100.0%** | **80.0%** | **100.0%** | **-20.0%** | **+20.0% (100%)** | Dữ liệu bị mất làm giảm khả năng retrieval |
| `mean_token_f1` | **68.8%** | **61.1%** | **68.8%** | **-7.7%** | **+7.7% (100%)** | Ký tự rác và rỗng summary giảm độ chính xác từ vựng |
| `judge_accuracy` | **80.0%** | **60.0%** | **80.0%** | **-20.0%** | **+20.0% (100%)** | LLM Judge đánh giá chất lượng câu trả lời sụt giảm |
| `mean_judge_score` | **3.6** | **3.2** | **3.6** | **-0.4** | **+0.4 (100%)** | Điểm trung bình sụt giảm rõ rệt trên dữ liệu bẩn |
| Quality checks pass/fail | **PASS** | **FAIL** | **PASS** | **Chuyển PASS $\rightarrow$ FAIL** | **Phục hồi PASS** | GX 1.x phát hiện chính xác dữ liệu vi phạm |
| Freshness status | **Fresh** | **Fresh** | **Fresh** | Tỷ lệ stale tăng | Phục hồi | SLA kiểm soát độ tươi mới của tri thức |

**Chuỗi nhân quả được hỗ trợ bởi artifacts:**
1. *Data corruption (xóa 20% bài mới + xóa abstract)* $\rightarrow$ *GX Quality check báo FAIL* $\rightarrow$ *Retrieval Hit Rate sụt giảm 20% và Token F1 giảm 7.7% (Silent Failure)*.
2. *Idempotent Repair (nạp lại từ Raw snapshot)* $\rightarrow$ *GX Quality check quay lại PASS* $\rightarrow$ *Retrieval Hit Rate và Token F1 phục hồi 100% về mức Baseline*.

---

## 11. Vấn đề tích hợp quan trọng

- **Triệu chứng:** Khi chạy lệnh in kiểm tra trên Windows PowerShell, Python ném lỗi `UnicodeEncodeError: 'charmap' codec can't encode character...`.
- **Nguyên nhân:** Console Windows PowerShell mặc định mã hóa `cp1252`, không hỗ trợ in ký tự tiếng Việt UTF-8.
- **Cách xử lý:** Đặt biến môi trường hệ thống `$env:PYTHONIOENCODING="utf-8"` trước khi thực thi lệnh Python.
- **Cách xác minh:** Lệnh in chạy thành công xuất chuỗi tiếng Việt trơn tru mà không có exception.

---

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng | Hướng cải thiện có thể kiểm chứng |
| --------------------- | -------------- | ----------------------------------------- |
| Chưa có giao diện giám sát trực quan | Khó quan sát xu hướng thay đổi chất lượng dữ liệu | Xây dựng Observability Dashboard với Streamlit/Gradio (Bonus B1) |
| Kiểm tra Freshness cố định ở 180 ngày | Chưa linh hoạt với các miền tri thức biến động nhanh | Cấu hình ngưỡng Freshness động theo từng chủ đề bài báo |

---

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm Beta và repository chính xác.
- [x] Phân công 2 thành viên khớp với module, artifact và kết quả thực tế.
- [x] Lệnh tái hiện đã được chạy lại thành công trên phiên bản dùng để nộp.
- [x] Baseline, corrupted và repaired dùng chung tập `data/eval/test_set.json`.
- [x] Bảng metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness conclusions khớp với `data/quality/`.
- [x] Các đường dẫn báo cáo và artifact truy cập được.
- [x] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng.
- [x] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
