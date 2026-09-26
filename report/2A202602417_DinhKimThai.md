# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | Đinh Kim Thái |
| **MSSV** | 2A202602417 |
| **Khóa/Lớp** | K4 - L3B (Ca Sáng) |
| **Tên nhóm** | Beta |
| **Vai trò chính** | Data Engineer / Data Observability Engineer |
| **Repository** | https://github.com/thaidinh1206/K4-L3B-DAY10-Beta-DataPipelineDataObservability |
| **Ngày hoàn thành** | 2026-09-26 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :---: |
| **Raw Ingestion & Lineage** | `src/ingestion/crossref.py`<br>- `parse_crossref_payload`<br>- `fetch_source_records`<br>- `load_raw_records` | Crossref REST API hoặc Snapshot `data/raw/crossref_response.json` | `data/raw/crossref_response.json`<br>`data/raw/crossref_records.json` | Hoàn thành |
| **Data Cleaning & Modeling** | `src/ingestion/cleaning.py`<br>- `build_clean_dataframe`<br>- `save_clean_dataframe` | 24 `PaperRecord` từ `data/raw/crossref_records.json` | `data/clean/papers_clean.csv`<br>`data/clean/papers_clean.json` | Hoàn thành |
| **Data Quality Gate (GX 1.x)** | `src/observability/quality.py`<br>- `run_data_quality_checks` | Clean DataFrame từ `papers_clean.json` | `data/quality/baseline_quality_report.json`<br>`data/quality/corrupted_quality_report.json` | Hoàn thành |
| **Freshness SLA Monitoring** | `src/observability/quality.py`<br>- `build_freshness_report` | Cột `age_days` trong DataFrame sạch / bẩn | `data/quality/freshness_report.json` | Hoàn thành |
| **Synthetic Data Corruption** | `src/ingestion/corruption.py`<br>- `corrupt_clean_dataframe`<br>- `save_corrupted_dataframe` | Clean DataFrame | `data/clean/papers_clean_corrupted.json`<br>`data/results/corruption_log.json` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| Thiết lập môi trường & encoding UTF-8 | Toàn nhóm / Terminal chạy lệnh | Thiết lập `$env:PYTHONIOENCODING="utf-8"`, sửa lỗi hiển thị tiếng Việt trên Windows PowerShell |
| Cung cấp schema chuẩn cho Vector Store | TV phụ trách RAG & Vector Index | Bàn giao cột `text_for_embedding` 5 phần giúp mô hình MiniLM tạo vector chính xác |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| **Thu thập & Chuẩn hóa thô** | `src/ingestion/crossref.py`<br>`data/raw/*` | 24 bản ghi `PaperRecord` sạch XML tag, có DOI, authors, dates | `python -c "... fetch_source_records ..."` in 24 bài |
| **Làm sạch & Pre-embed** | `src/ingestion/cleaning.py`<br>`data/clean/*` | Clean DataFrame 24 dòng có `text_for_embedding` và `age_days` | `python -c "... build_clean_dataframe ..."` clean 24 dòng |
| **Quality Gate GX 1.x** | `src/observability/quality.py`<br>`data/quality/*` | Bộ 4 Expectations thiết yếu, kết quả baseline `success=True` | `run_data_quality_checks` xuất JSON report đạt chuẩn |
| **Freshness SLA** | `src/observability/quality.py`<br>`freshness_report.json` | Tỷ lệ stale 4.17% <= 25% $\rightarrow$ `is_fresh=True` | `build_freshness_report` ghi nhận đúng `is_fresh: true` |
| **Tiêm lỗi dữ liệu** | `src/ingestion/corruption.py`<br>`corruption_log.json` | Tiêm đủ 6 dạng lỗi, làm GX báo Fail và Freshness báo False | Xuất `corruption_log.json` ghi nhận đủ 6 kịch bản |

**Output cụ thể tiêu biểu:**
1. File `data/clean/papers_clean.json` chứa 24 bài báo với trường `text_for_embedding` cấu trúc 5 phần (`Title`, `Authors`, `Published`, `Abstract`, `Categories`) và trường `age_days` làm thước đo độ tươi mới.
2. File `data/quality/baseline_quality_report.json` với 100% Expectations passed theo chuẩn Great Expectations 1.x Ephemeral context.

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
1. **Lỗi ngầm (Silent Failure) trong RAG:** Nếu dữ liệu bị bẩn (mất tóm tắt, tiêu đề ngắn, bị trùng lặp, hoặc bị quá hạn), hệ thống thông thường không báo exception nhưng LLM sẽ hallucinate hoặc trả lời sai. Cần xây dựng chốt chặn tự động.
2. **Dữ liệu Crossref thô chứa nhiều nhiễu:** Abstract chứa thẻ XML (`<jats:p>`), tác giả phân mảnh theo cấu trúc object lồng ghép, ngày xuất bản nằm sâu trong mảng `date-parts`.
3. **Độ tươi mới (Data Freshness):** Tri thức khoa học cần cập nhật; các bài báo quá cũ cần được phát hiện để cảnh báo người dùng.

### Cách triển khai
1. **Pipeline Ingestion (`crossref.py`):**
   - Viết regex `re.sub(r"<[^>]+>", "", text)` để bóc tách triệt để thẻ JATS XML.
   - Ghép họ tên tác giả `f"{given} {family}"` và chuẩn hóa ngày tháng `YYYY-MM-DD`.
   - Cơ chế offline fallback: tự động nạp snapshot `crossref_response.json` khi `REFRESH_SOURCE=false` hoặc khi gặp lỗi mạng/429.
2. **Data Cleaning & Modeling (`cleaning.py`):**
   - Khử trùng lặp theo `paper_id` bằng `drop_duplicates(subset=["paper_id"])`.
   - Tính toán độ tuổi tài liệu: `age_days = (run_date - pub_dates).dt.days` đồng bộ timezone UTC.
   - Ghép trường `text_for_embedding` chuẩn 5 phần để tối ưu hóa vector retrieval.
3. **Data Observability (`quality.py`):**
   - Sử dụng chuẩn mới **Great Expectations 1.x Ephemeral Context**:
     - `context = gx.get_context(mode="ephemeral")`
     - Khởi tạo pandas data asset và batch definition.
   - 4 Expectations thiết yếu:
     - `ExpectTableRowCountToBeBetween(10, 100)`
     - `ExpectColumnValuesToNotBeNull("paper_id", "title", "text_for_embedding")`
     - `ExpectColumnValuesToBeUnique("paper_id")`
     - `ExpectColumnValueLengthsToBeBetween("title", 8, 500)` và `ExpectColumnValueLengthsToBeBetween("summary", 20, 5000)`
   - Freshness SLA: Cảnh báo `is_fresh = False` nếu tỷ lệ bài báo có `age_days > 180` vượt quá 25%.

### Input, output và contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | `data/raw/crossref_response.json` (payload gốc 24 bài báo) |
| **Output** | `data/raw/crossref_records.json`, `data/clean/papers_clean.json`, `data/quality/*` |
| **Module phụ thuộc** | `core/config.py`, `core/utils.py` |
| **Module sử dụng output** | `retrieval/index.py` (ChromaDB), `evaluation/testset.py`, `pipelines/phase1.py` |
| **Xử lý ngoại lệ** | Fallback snapshot local khi mất mạng, parse an toàn khi thiếu abstract hoặc thiếu author |

### Cách xác minh

```bash
# 1. Xác minh Ingestion
$env:PYTHONIOENCODING="utf-8"
python -c "import sys; sys.path.insert(0, 'src'); from core.config import load_settings; from ingestion.crossref import fetch_source_records; s=load_settings(); r=fetch_source_records(s); print(f'Tín hiệu hoàn thành: Đã tải {len(r)} bài báo')"

# 2. Xác minh Cleaning
python -c "import sys; sys.path.insert(0, 'src'); from datetime import datetime, timezone; from core.config import load_settings; from ingestion.crossref import load_raw_records; from ingestion.cleaning import build_clean_dataframe, save_clean_dataframe; s=load_settings(); records=load_raw_records(s.paths.raw_records_json); df=build_clean_dataframe(records, datetime.now(timezone.utc)); save_clean_dataframe(df, s); print(f'Tín hiệu hoàn thành: Clean thành công {len(df)} dòng')"

# 3. Xác minh Quality Gate & Freshness SLA
python -c "import sys; sys.path.insert(0, 'src'); from core.config import load_settings; from observability.quality import run_data_quality_checks, build_freshness_report; import pandas as pd; s=load_settings(); df=pd.read_json(s.paths.clean_json); res=run_data_quality_checks(df, s, 'baseline'); f_res=build_freshness_report(df, s); print('Tín hiệu hoàn thành: Quality check status =', res['success'], ', is_fresh =', f_res['is_fresh'])"
```

- **Kết quả mong đợi & thực tế:** 
  - `Tín hiệu hoàn thành: Đã tải 24 bài báo`
  - `Tín hiệu hoàn thành: Clean thành công 24 dòng`
  - `Tín hiệu hoàn thành: Quality check status = True , is_fresh = True`

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Thu thập dữ liệu từ Crossref API công cộng trong phòng lab thi tập trung.
- **Các phương án đã cân nhắc:**
  - *Phương án A:* Luôn gửi request trực tiếp ra internet tới `api.crossref.org`.
  - *Phương án B (Đã chọn):* Hỗ trợ cơ chế Offline Snapshot Fallback thông qua cờ cấu hình `REFRESH_SOURCE`.
- **Lý do chọn:** Crossref public API áp dụng rate limit nghiêm ngặt (`429 Too Many Requests`). Phương án B vừa cho phép tải dữ liệu thật khi cần, vừa bảo vệ pipeline hoạt động ổn định 100% offline, đảm bảo tính tái lập (Reproducibility) và Data Lineage theo đúng chuẩn Rubric.
- **Bằng chứng:** Hệ thống khởi tạo và hoàn tất CP0 chỉ trong 2 giây mà không gặp bất kỳ lỗi kết nối mạng nào.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  UnicodeEncodeError: 'charmap' codec can't encode character '\u1ec7' in position 6: character maps to <undefined>
  ```
- **Lệnh/bước tái hiện:** Chạy lệnh Python in chuỗi tiếng Việt `Tín hiệu hoàn thành...` trên terminal PowerShell mặc định của Windows.
- **Nguyên nhân gốc:** Bảng mã mặc định của console Windows là `cp1252`, không hỗ trợ ký tự UTF-8 tiếng Việt có dấu.
- **Cách xử lý:** Đặt biến môi trường hệ thống `$env:PYTHONIOENCODING="utf-8"` trước khi chạy lệnh Python.
- **Cách xác minh sau khi sửa:** Chạy lại lệnh in, console hiển thị trơn tru: `Tín hiệu hoàn thành: Đã tải 24 bài báo`.
- **Điều học được:** Luôn chú ý cấu hình UTF-8 encoding trên môi trường Windows đa nền tảng trong các pipeline xử lý ngôn ngữ tự nhiên.

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**  
   Dữ liệu thô từ Crossref API/Snapshot được trích xuất thành danh sách `PaperRecord` qua `crossref.py`. Sau đó, `cleaning.py` khử trùng lặp theo `paper_id`, tính `age_days` và ghép chuỗi 5 phần `text_for_embedding`. Dữ liệu sạch đi qua `quality.py` để kiểm định. Khi đạt chuẩn (`success=True`), văn bản được chuyển sang mô hình `sentence-transformers/all-MiniLM-L6-v2` để sinh vector 384 chiều và nạp vào collection `papers-baseline` trong ChromaDB.

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**  
   Mỗi câu hỏi kiểm thử trong test set có một `ground_truth_doc_id` xác định bài báo chứa đáp án. Khi RAG truy vấn top-k văn bản, `retrieval_hit_rate` được tính bằng tỷ lệ số câu hỏi mà top-k kết quả có chứa đúng `ground_truth_doc_id`. Sau đó, LLM sinh câu trả lời và đo lường độ trùng khớp từ vựng qua `token_f1` so với ground truth.

3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**  
   - *Quality checks (GX 1.x)* kiểm soát cấu trúc và tính toàn vẹn tĩnh của dữ liệu (schema validation, non-null, uniqueness, độ dài văn bản).
   - *Freshness monitoring* kiểm soát tính hợp thời động của tri thức theo thời gian thực (đo lường `age_days` và tỷ lệ tài liệu quá hạn so với ngưỡng Freshness SLA 180 ngày).

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**  
   Để đảm bảo tính khoa học và biến số kiểm soát (Controlled Experiment). Khi giữ nguyên tập câu hỏi đánh giá, sự sụt giảm hay phục hồi của `retrieval_hit_rate` và `token_f1` hoàn toàn phản ánh trung thực tác động của chất lượng dữ liệu, loại bỏ sai số do độ khó của câu hỏi gây ra.

5. **Repair được xem là thành công dựa trên artifact và metric nào?**  
   Repair thành công khi:
   - Dữ liệu khôi phục sạch sẽ từ bản raw snapshot gốc (`data/raw/crossref_records.json`).
   - Báo cáo chất lượng `repaired_quality_report.json` đạt `success: true` và `freshness_report.json` đạt `is_fresh: true`.
   - Các chỉ số hiệu năng trên `repaired_metrics.json` (Hit Rate, Token F1) phục hồi trở lại tương đương với `baseline_metrics.json`.

---

## 8. Phân tích kết quả

### Metrics chính (Dữ liệu Observability)

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| :--- | :---: | :---: | :---: | :--- |
| **Quality checks (GX 1.x)** | **PASS (True)** | **FAIL (False)** | **PASS (True)** | Chốt kiểm dịch phát hiện chính xác lỗi null, độ dài ngắn và trùng lặp |
| **Freshness status** | **Fresh (True)** | **Stale (False)** | **Fresh (True)** | Freshness SLA cảnh báo ngay khi 40% bài báo bị lùi ngày xuất bản |
| **Total valid records** | 24 | 19 (mất 5 bài mới) | 24 | Khôi phục trọn vẹn số lượng bài báo ban đầu |

### Kết luận từ số liệu
1. **[Data corruption] $\rightarrow$ [Quality/Freshness signal thay đổi]:** Khi tiêm lỗi cắt ngắn tiêu đề và xóa tóm tắt, GX 1.x lập tức báo `success=False` do vi phạm độ dài tối thiểu. Khi lùi ngày xuất bản của 40% bài báo, tỷ lệ quá hạn đạt 40% > 25%, kích hoạt cảnh báo vi phạm Freshness SLA (`is_fresh=False`).
2. **[Idempotent Repair] $\rightarrow$ [Khôi phục hoàn toàn]:** Việc nạp lại từ nguồn Raw Snapshot nguyên bản cho phép tái tạo 100% dữ liệu sạch mà không bị phụ thuộc mạng bên ngoài, đưa mọi chỉ số Observability trở lại trạng thái hoàn hảo.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Kiến trúc Data Lineage & Idempotence:** Tầm quan trọng của việc lưu trữ snapshot thô nguyên bản bất biến (Source of Truth) để làm điểm tựa tự phục hồi dữ liệu khi có sự cố.
2. **Cơ chế Data Observability hiện đại:** Cách triển khai Ephemeral context với Great Expectations 1.x giúp tự động hóa khâu kiểm định chất lượng mà không làm nặng hạ tầng.
3. **Mối quan hệ mật thiết giữa Data Quality và AI Performance:** Thấy rõ hiện tượng Silent Failure – AI trả lời sai không phải do mô hình LLM kém mà do dữ liệu đầu vào bị suy giảm chất lượng.

### Nếu có thêm thời gian
Xây dựng một giao diện Web Dashboard thời gian thực (bằng Streamlit) hiển thị biểu đồ phân bố `age_days` của bài báo và trạng thái đèn xanh/đỏ của các Quality Expectations để lấy trọn vẹn điểm thưởng Bonus B1 (+5 điểm).

---

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Đinh Kim Thái  
**Ngày xác nhận:** 2026-09-26
