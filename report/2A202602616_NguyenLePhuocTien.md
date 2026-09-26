# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                                                                                                       |
| ------------------ | --------------------------------------------------------------------------------------------------------------- |
| Họ và tên       | Nguyễn Lê Phước Tiến                                                                                       |
| MSSV               | 2A202602616                                                                                                     |
| Khóa/Lớp         | K4                                                                                                              |
| Tên nhóm         | Beta                                                                                                            |
| Vai trò chính    | Evaluation Dataset · Embedding · ChromaDB · Baseline/Corrupted/Repaired Evaluation · Metrics · Reports/Integration |
| Repository         | https://github.com/thaidinh1206/K4-L3B-DAY10-Beta-DataPipelineDataObservability                                |
| Ngày hoàn thành | 2026-09-26                                                                                                      |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable      | File/hàm phụ trách                                                    | Input nhận vào                              | Output bàn giao                                                    | Trạng thái   |
| ----------------------- | ---------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------- | ------------- |
| Evaluation Test Set     | `src/evaluation/testset.py` · `build_test_set()`                     | `papers_clean.json` (DataFrame 24 dòng)    | `data/eval/test_set.json` (10 câu hỏi, 4 loại)                  | Hoàn thành   |
| Baseline Pipeline       | `src/pipelines/phase1.py` · `run_phase1_pipeline()`                  | `crossref_records.json`                      | `papers_clean.csv`, `baseline_metrics.json`, `phase1_report.md`   | Hoàn thành   |
| ChromaDB Indexing       | `src/retrieval/index.py` · `LocalEmbeddingIndex.build()`             | Clean DataFrame + embedding model            | ChromaDB collections: baseline / corrupted / repaired              | Hoàn thành   |
| Baseline Evaluation     | `src/evaluation/metrics.py` · `evaluate_pipeline()`                  | `test_set.json` + ChromaDB index             | `baseline_metrics.json`, `baseline_answers.json`                   | Hoàn thành   |
| Corruption Flow         | `src/pipelines/corruption_flow.py` · `run_corruption_flow_pipeline()` | `papers_clean.json`, `baseline_metrics.json` | `corrupted_metrics.json`, `repaired_metrics.json`, `corruption_report.md` | Hoàn thành   |
| Reports                 | `src/observability/reporting.py` · `generate_phase1_report()`, `generate_corruption_report()` | metrics + quality + freshness dicts | `phase1_report.md`, `corruption_report.md`         | Hoàn thành   |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả và bằng chứng |
| ---------- | ----------------------------- | ---------------------- |
| Implement `corrupt_clean_dataframe()` với đủ 6 loại lỗi | `src/ingestion/corruption.py` | `corruption_log.json` ghi đủ 6 entries; pipeline corruption_flow chạy end-to-end |
| Implement `build_clean_dataframe()`, `load_raw_records()` | `src/ingestion/cleaning.py`, `crossref.py` | `papers_clean.csv` 24 dòng sạch; pipeline phase1 chạy thành công |
| Implement `run_data_quality_checks()`, `build_freshness_report()` | `src/observability/quality.py` | Quality gate PASSED baseline/repaired, FAILED corrupted (đúng kỳ vọng) |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện                     | File/artifact liên quan                       | Kết quả bàn giao                                   | Cách xác minh                                                             |
| ------------------------------------------ | --------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------- |
| Sinh 10 câu hỏi test set (4 loại)         | `src/evaluation/testset.py`                  | `data/eval/test_set.json`                           | Console in `Tín hiệu hoàn thành: Sinh được 10 câu hỏi test`            |
| Chạy baseline pipeline end-to-end         | `src/pipelines/phase1.py`                    | `baseline_metrics.json`, `phase1_report.md`         | `python script/run_phase1.py` exit code 0                                 |
| Index 3 ChromaDB collections               | `src/retrieval/index.py`                     | `data/chroma/` (baseline / corrupted / repaired)    | `data/embeddings/papers_embeddings*.json` tồn tại                        |
| Đo suy giảm khi data bị corrupt           | `src/pipelines/corruption_flow.py`           | `corrupted_metrics.json`                            | hit_rate giảm `1.000 → 0.800`, f1 giảm `0.688 → 0.611`                  |
| Xác minh phục hồi sau idempotent repair   | `src/pipelines/corruption_flow.py`           | `repaired_metrics.json`                             | hit_rate phục hồi `0.800 → 1.000`, f1 phục hồi `0.611 → 0.688`          |
| Xuất báo cáo so sánh 3 trạng thái         | `src/observability/reporting.py`             | `data/reports/corruption_report.md`                 | Bảng Baseline vs Corrupted vs Repaired đủ 3 cột, in ra console           |

**Output cụ thể:** `data/results/baseline_metrics.json` ghi `retrieval_hit_rate: 1.0`, `mean_token_f1: 0.688` trên 10 câu hỏi test. `corruption_report.md` thể hiện rõ degradation khi corrupt và recovery hoàn toàn sau repair, chứng minh cơ chế idempotent repair hoạt động đúng.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Phần của tôi giải quyết bài toán **đo lường chất lượng RAG pipeline qua 3 trạng thái dữ liệu** — baseline sạch, dữ liệu bị corrupt, và sau khi repair — để chứng minh hiện tượng Silent Failure và khả năng tự phục hồi của hệ thống.

### Cách triển khai

**Evaluation test set (`build_test_set`):** Chọn 10 paper đại diện bằng cách lấy mẫu đều qua toàn bộ corpus (bước `total // 10`). Sinh câu hỏi theo 4 loại xoay vòng: `summary`, `authors`, `date`, `categories`. Ground truth lấy trực tiếp từ các cột có cấu trúc của DataFrame — không dùng LLM để sinh ground truth, đảm bảo tính xác định và tái tạo được.

**Baseline pipeline (`run_phase1_pipeline`):** Xâu chuỗi 7 bước: Ingest → Clean → Index ChromaDB (model `all-MiniLM-L6-v2`, cosine similarity) → Sinh test set → Evaluate (retrieval hit rate + token F1 + LLM judge) → GX Quality Gate + Freshness SLA → Sinh `phase1_report.md`.

**Corruption flow (`run_corruption_flow_pipeline`):** Load baseline → Inject 6 loại lỗi vào clean DataFrame → Index ChromaDB corrupted → Đo degradation → Gọi `repair_from_raw_snapshot()` (rebuild từ `crossref_records.json`, không từ corrupted data) → Index ChromaDB repaired → Đánh giá lại → Sinh bảng so sánh 3 cột.

**Idempotent repair (`repair_from_raw_snapshot`):** Luôn đọc từ `data/raw/crossref_records.json` và chạy lại toàn bộ cleaning pipeline từ đầu — không có state từ corrupted data. Chạy N lần cho cùng kết quả sạch.

### Input, output và contract

| Thành phần                | Mô tả                                                                                                     |
| -------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Input                      | `papers_clean.json` — DataFrame 24 dòng, cột: `paper_id`, `title`, `summary`, `authors_joined`, `categories_joined`, `published`, `text_for_embedding` |
| Output                     | `test_set.json` (10 items), `baseline/corrupted/repaired_metrics.json`, `phase1_report.md`, `corruption_report.md` |
| Module phụ thuộc          | `ingestion.crossref`, `ingestion.cleaning`, `observability.quality` (Member 1)                            |
| Module sử dụng output     | `script/run_phase1.py`, `script/run_corruption_flow.py`                                                   |
| Điều kiện lỗi cần xử lý | `papers_clean.json` không tồn tại → pipeline báo lỗi rõ; ChromaDB collection đã tồn tại → delete và recreate trước khi index |

### Cách xác minh

```bash
# Nhiệm vụ 1 — test set
python -c "from core.config import load_settings; from evaluation.testset import build_test_set; import pandas as pd; s=load_settings(); df=pd.read_json(s.paths.clean_json); ts=build_test_set(df, s.paths.eval_testset); print(f'Tín hiệu hoàn thành: Sinh được {len(ts)} câu hỏi test')"

# Nhiệm vụ 2 — phase 1
python script/run_phase1.py

# Nhiệm vụ 3 — corruption
python -c "from core.config import load_settings; from ingestion.corruption import corrupt_clean_dataframe; import pandas as pd; s=load_settings(); df=pd.read_json(s.paths.clean_json); c=corrupt_clean_dataframe(df, s.paths.corruption_log); print(f'Tín hiệu hoàn thành: Corrupted {len(c)} dòng')"

# Nhiệm vụ 4 — corruption flow
python script/run_corruption_flow.py
```

- **Kết quả mong đợi:** Console in đúng các chuỗi tín hiệu hoàn thành; artifacts sinh ra đầy đủ.
- **Kết quả thực tế:** Tất cả 4 tín hiệu pass. `retrieval_hit_rate` baseline = 1.000, corrupted = 0.800, repaired = 1.000.
- **Artifact/log:** `data/results/baseline_metrics.json`, `data/results/corrupted_metrics.json`, `data/results/repaired_metrics.json`, `data/reports/corruption_report.md`.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi thiết kế `repair_from_raw_snapshot()`, cần chọn nguồn dữ liệu để repair — dùng corrupted DataFrame đã lưu hay raw snapshot gốc.
- **Các phương án đã cân nhắc:**
  1. Dùng `papers_clean_corrupted.json` làm nguồn, cố gắng "vá" từng loại lỗi đã biết.
  2. Rebuild hoàn toàn từ `data/raw/crossref_records.json` qua toàn bộ cleaning pipeline.
- **Phương án đã chọn:** Phương án 2 — rebuild từ raw snapshot.
- **Lý do:** Phương án 1 không idempotent — kết quả phụ thuộc vào state của corrupted data, khó đảm bảo loại bỏ hết tất cả lỗi đã tiêm vào (đặc biệt duplicate rows và noise ký tự). Phương án 2 đảm bảo tính idempotent: chạy bao nhiêu lần cũng cho cùng kết quả sạch, đúng thiết kế self-healing pipeline trong production.
- **Bằng chứng quyết định phù hợp:** Sau repair, `retrieval_hit_rate` phục hồi về đúng 1.000 (bằng baseline), quality gate PASSED, freshness SLA OK — chứng minh rebuild hoàn toàn hoạt động đúng và đủ.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```
  ! [rejected] tiennguyen -> tiennguyen (non-fast-forward)
  error: failed to push some refs to 'https://github.com/...'
  hint: Updates were rejected because the tip of your current branch is behind
  ```
- **Lệnh tái hiện:** `git push origin tiennguyen`
- **Nguyên nhân gốc:** Remote branch `tiennguyen` đã có commits mới (được merge từ Member 1 vào main rồi sync sang) sau khi tôi tạo commit local, khiến local branch bị diverge — local và remote có lịch sử không cùng ancestor tuyến tính.
- **Cách xử lý:**
  ```bash
  git fetch origin
  git rebase origin/tiennguyen
  # resolve conflicts: git checkout --ours <files>
  git add <conflicted_files>
  GIT_EDITOR=true git rebase --continue
  git push origin tiennguyen
  ```
- **Cách xác minh sau khi sửa:** Push thành công với output `1c06e32..0562d8b tiennguyen -> tiennguyen`, exit code 0.
- **Điều học được:** Trong teamwork với shared branch, luôn `git fetch` và `git rebase origin/<branch>` trước khi push. Dùng `--ours`/`--theirs` khi resolve conflict có chủ đích — `--ours` giữ version local (phần mình đã implement), `--theirs` lấy version remote.

## 7. Hiểu biết về luồng end-to-end

**Câu trả lời:**

1. **Crossref đến vector index:** Crossref API (hoặc fallback `crossref_records.json`) → `parse_crossref_payload()` / `load_raw_records()` ra list `PaperRecord` → `build_clean_dataframe()` normalize text, tính `age_days`, ghép `text_for_embedding = "Title: ... Authors: ... Summary: ..."` → `LocalEmbeddingIndex.build()` encode bằng `all-MiniLM-L6-v2` (384 chiều, cosine) → lưu vào ChromaDB PersistentClient.

2. **Evaluation set và ground-truth doc IDs:** `build_test_set()` tạo 10 câu hỏi với `ground_truth_doc_ids = [paper_id]`. Khi evaluate, `answer_question()` dùng ChromaDB để tìm top-k docs và trả về `retrieved_doc_ids`. `retrieval_hit = any(doc_id in ground_truth_doc_ids for doc_id in retrieved_doc_ids)` — hit nếu ít nhất 1 trong top-4 chứa đúng paper. `mean_token_f1` đo overlap token giữa câu trả lời và ground truth text (không phân biệt hoa thường).

3. **Quality checks vs Freshness monitoring:** GX Quality checks kiểm tra **tính hợp lệ của cấu trúc dữ liệu** tại một thời điểm — null check, unique constraint, độ dài summary. Freshness monitoring kiểm tra **chiều thời gian** — tỉ lệ bài báo có `age_days > 180`; nếu > 25% thì `is_fresh = False`. GX phát hiện lỗi cấu trúc ngay lập tức, Freshness phát hiện data staleness theo thời gian — hai cơ chế bổ sung nhau.

4. **Cùng test set cho 3 trạng thái:** Đảm bảo so sánh "apple to apple" — thay đổi metric chỉ phản ánh thay đổi chất lượng dữ liệu/index, không do câu hỏi khác nhau. Nếu dùng test set khác nhau, không thể kết luận metric giảm là do corruption hay do câu hỏi khó hơn.

5. **Repair thành công khi:** (a) **Artifact**: `repaired_clean.csv` có đủ 24 dòng sạch, `repaired_metrics.json` tồn tại; (b) **Metrics**: `retrieval_hit_rate` và `mean_token_f1` bằng baseline; (c) **Quality gate**: GX PASSED trên repaired data; (d) **Freshness**: `is_fresh = True`. Tất cả 4 điều kiện này đều đúng sau khi chạy `repair_from_raw_snapshot()`.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân                                                                       |
| ---------------------- | -------: | --------: | -------: | ------------------------------------------------------------------------------------------- |
| `retrieval_hit_rate`   | 1.000    | 0.800     | 1.000    | Giảm 20pp khi corrupt (2/10 câu miss); phục hồi hoàn toàn sau repair                      |
| `mean_token_f1`        | 0.688    | 0.611     | 0.688    | Giảm ~7.7pp do title truncate và summary noise làm lệch embedding vector                   |
| `judge_accuracy`       | 0.800    | 0.600     | 0.800    | LLM judge nhận ra câu trả lời kém hơn khi data hỏng; phục hồi đúng về baseline            |
| `mean_judge_score`     | 3.6/5    | 3.2/5     | 3.6/5    | Nhất quán với `judge_accuracy`; không có regression sau repair                             |
| Quality checks         | PASSED   | FAILED    | PASSED   | GX phát hiện đúng: blank summary vi phạm `ExpectColumnValueLengthsToBeBetween(10, 5000)`  |
| Freshness status       | Fresh    | Fresh     | Fresh    | Stale date chỉ affect 2/20 rows (~9%), dưới ngưỡng 25% nên SLA vẫn `is_fresh = True`     |

### Kết luận từ số liệu

1. **[Data corruption]** tiêm 6 loại lỗi → **[GX quality gate FAILED]** (blank summary vi phạm length expectation, duplicate rows tăng row count bất thường) → **[hit_rate giảm 1.000 → 0.800, token_f1 giảm 0.688 → 0.611]** vì embedding của corrupted text không còn gần với query embedding (Silent Failure — pipeline không throw exception).

2. **[Repair action]** `repair_from_raw_snapshot()` rebuild từ `crossref_records.json` → **[GX quality gate PASSED, freshness `is_fresh = True`]** → **[hit_rate phục hồi 1.000, token_f1 phục hồi 0.688]** — xác nhận idempotent repair hiệu quả và đầy đủ.

**Corruption ảnh hưởng rõ nhất:** `blank_summary` và `inject_noise` — vì `text_for_embedding` phụ thuộc nặng vào nội dung summary. Khi summary bị xóa hoặc nhiễu ký tự rác, embedding vector lệch xa query vector dẫn đến retrieval miss.

**Kết quả khác kỳ vọng:** Freshness SLA vẫn `is_fresh = True` dù có inject stale date — chỉ 2/20 rows (~9%) bị stale, dưới ngưỡng 25%. Điều này cho thấy Freshness SLA không đủ nhạy với corruption nhỏ; cần bổ sung metric như median age hoặc p90 age để phát hiện sớm hơn.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Data pipeline:** Idempotent repair phải rebuild từ nguồn raw gốc — không "vá" từ data đã corrupt, vì không thể đảm bảo loại bỏ hết tất cả lỗi đã tiêm vào. Raw snapshot là single source of truth.

2. **Data quality/observability:** GX Quality Gate và Freshness SLA bổ sung cho nhau nhưng không thay thế nhau. GX phát hiện lỗi cấu trúc ngay lập tức (structural correctness), Freshness phát hiện data drift theo thời gian (temporal freshness). Cần cả hai để có observability toàn diện.

3. **RAG agent:** Silent Failure là rủi ro thực trong production — pipeline không crash nhưng answer quality giảm ngầm. Chỉ có Continuous Benchmark Evaluation (đo hit rate, f1 định kỳ) mới phát hiện được sự suy giảm này trước khi người dùng phàn nàn.

### Nếu có thêm thời gian

Cải thiện test set bằng LLM để sinh câu hỏi multi-hop và so sánh (e.g. "So sánh phương pháp của paper A và paper B"). Test set hiện tại quá đơn giản — baseline hit_rate = 1.000 không để lại headroom để thấy sự khác biệt tinh tế giữa corrupted và baseline. Câu hỏi phức tạp hơn sẽ làm lộ rõ hơn mức độ degradation thực sự.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Lê Phước Tiến
**Ngày xác nhận:** 2026-09-26
