# Member Role Report — Day 10: Data Pipeline & Data Observability

> Mỗi thành viên trong nhóm tự hoàn thành mẫu này để báo cáo đúng vai trò, phần việc và mức hiểu của mình. Không sao chép nguyên báo cáo chung hoặc báo cáo của thành viên khác.

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------- |
| Họ và tên       | Nguyễn Lê Phước Tiến                                                                   |
| MSSV               | 2A202602616                                                                                 |
| Khóa/Lớp         | K4                                                                                          |
| Tên nhóm         | Beta                                                                                        |
| Vai trò chính    | Evaluation Dataset · Embedding · ChromaDB · RAG Agent · Baseline/Corrupted/Repaired Eval · Metrics · Reports |
| Repository         | https://github.com/thaidinh1206/K4-L3B-DAY10-Beta-DataPipelineDataObservability            |
| Ngày hoàn thành | 2026-09-26                                                                                  |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| ------------------ | ------------------- | ---------------- | ---------------- | ----------- |
| Evaluation Test Set | `src/evaluation/testset.py` · `build_test_set()` | `papers_clean.json` (DataFrame 24 dòng) | `data/eval/test_set.json` (10 câu hỏi, 4 loại) | Hoàn thành |
| Baseline Pipeline | `src/pipelines/phase1.py` · `run_phase1_pipeline()` | `crossref_records.json` | `papers_clean.csv`, `baseline_metrics.json`, `phase1_report.md` | Hoàn thành |
| ChromaDB Indexing | `src/retrieval/index.py` · `LocalEmbeddingIndex.build()` | Clean DataFrame | ChromaDB collection `papers-baseline` | Hoàn thành |
| Baseline Evaluation | `src/evaluation/metrics.py` · `evaluate_pipeline()` | `test_set.json` + ChromaDB index | `baseline_metrics.json`, `baseline_answers.json` | Hoàn thành |
| Corruption Flow | `src/pipelines/corruption_flow.py` · `run_corruption_flow_pipeline()` | `papers_clean.json`, `baseline_metrics.json` | `corrupted_metrics.json`, `repaired_metrics.json`, `corruption_report.md` | Hoàn thành |
| Reports | `src/observability/reporting.py` · `generate_phase1_report()`, `generate_corruption_report()` | metrics + quality + freshness dicts | `phase1_report.md`, `corruption_report.md` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| ---------- | ----------------------------- | -------- |
| Implement `corrupt_clean_dataframe()` với đủ 6 loại lỗi | Module `src/ingestion/corruption.py` (phần Member 1) | `corruption_log.json` ghi đủ 6 entries; pipeline corruption_flow chạy end-to-end |
| Implement `build_clean_dataframe()`, `load_raw_records()` | Module `src/ingestion/cleaning.py`, `crossref.py` (phần Member 1) | `papers_clean.csv` 24 dòng sạch; pipeline phase1 chạy thành công |
| Implement `run_data_quality_checks()`, `build_freshness_report()` | Module `src/observability/quality.py` (phần Member 1) | Quality gate PASSED baseline/repaired, FAILED corrupted (đúng kỳ vọng) |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| ---------------------- | ---------------------------- | ---------------- | -------------- |
| Sinh 10 câu hỏi test set | `src/evaluation/testset.py` | `data/eval/test_set.json` | `python -c "...build_test_set..."; in "Tín hiệu hoàn thành: Sinh được 10 câu hỏi test"` |
| Chạy baseline pipeline end-to-end | `src/pipelines/phase1.py` | `baseline_metrics.json`, `phase1_report.md` | `python script/run_phase1.py` |
| Đo suy giảm khi data bị corrupt | `src/pipelines/corruption_flow.py` | `corrupted_metrics.json` | hit_rate giảm `1.000 → 0.800`, f1 giảm `0.688 → 0.611` |
| Xác minh phục hồi sau repair | `src/pipelines/corruption_flow.py` | `repaired_metrics.json` | hit_rate phục hồi `0.800 → 1.000`, f1 phục hồi `0.611 → 0.688` |
| Xuất báo cáo so sánh 3 trạng thái | `src/observability/reporting.py` | `data/reports/corruption_report.md` | Bảng Baseline vs Corrupted vs Repaired đủ 3 cột |

**Output cụ thể:** `data/results/baseline_metrics.json` ghi `retrieval_hit_rate: 1.0`, `mean_token_f1: 0.688` trên 10 câu hỏi test; `corruption_report.md` thể hiện rõ degradation khi corrupt và recovery sau repair, chứng minh cơ chế idempotent repair hoạt động đúng.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Phần của tôi giải quyết bài toán **đo lường chất lượng RAG pipeline theo 3 trạng thái dữ liệu**: baseline sạch, dữ liệu bị corrupt, và sau khi repair — để chứng minh hiện tượng Silent Failure và khả năng tự phục hồi của hệ thống.

### Cách triển khai

**Evaluation test set (`build_test_set`):** Chọn 10 paper đại diện (bước đều qua corpus), sinh câu hỏi theo 4 loại (summary, authors, date, categories) xoay vòng. Ground truth lấy trực tiếp từ các cột có cấu trúc của DataFrame (không dùng LLM để sinh ground truth), đảm bảo tính xác định và có thể tái tạo.

**Pipeline phase1 (`run_phase1_pipeline`):** Xâu chuỗi 7 bước: Ingest → Clean → Index ChromaDB (MiniLM-L6-v2 embedding, cosine similarity) → Sinh test set → Evaluate (retrieval hit rate + token F1 + LLM judge) → GX Quality Gate → Freshness SLA → Sinh báo cáo markdown.

**Corruption flow (`run_corruption_flow_pipeline`):** Load baseline → Inject 6 loại lỗi vào clean DataFrame → Index corrupted ChromaDB → Đo degradation → Gọi `repair_from_raw_snapshot()` (rebuild từ raw JSON, không từ corrupted) → Index repaired ChromaDB → Đánh giá lại → Sinh bảng so sánh 3 cột.

**Idempotent repair:** Hàm `repair_from_raw_snapshot()` luôn đọc từ `data/raw/crossref_records.json` và chạy lại toàn bộ cleaning pipeline — không có state từ corrupted data, đảm bảo chạy N lần cho cùng kết quả.

### Input, output và contract

| Thành phần | Mô tả |
| ----------- | ------ |
| Input | `papers_clean.json` (DataFrame 24 dòng, có cột: `paper_id`, `title`, `summary`, `authors_joined`, `categories_joined`, `published`, `text_for_embedding`) |
| Output | `test_set.json` (10 items), `baseline/corrupted/repaired_metrics.json`, `phase1_report.md`, `corruption_report.md` |
| Module phụ thuộc | `ingestion.crossref`, `ingestion.cleaning`, `observability.quality` (Member 1) |
| Module sử dụng output | `script/run_phase1.py`, `script/run_corruption_flow.py` |
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

- **Kết quả mong đợi:** Console in đúng chuỗi tín hiệu hoàn thành; artifacts sinh ra đầy đủ.
- **Kết quả thực tế:** Tất cả 4 tín hiệu pass; `retrieval_hit_rate` baseline = 1.000, corrupted = 0.800, repaired = 1.000.
- **Artifact/log:** `data/results/baseline_metrics.json`, `data/results/corrupted_metrics.json`, `data/results/repaired_metrics.json`, `data/reports/corruption_report.md`.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi thiết kế `repair_from_raw_snapshot()`, cần quyết định nguồn dữ liệu để repair — dùng corrupted DataFrame đã lưu hay raw snapshot gốc.
- **Các phương án đã cân nhắc:**
  1. Dùng `papers_clean_corrupted.json` làm nguồn, cố gắng "vá" từng lỗi.
  2. Rebuild hoàn toàn từ `data/raw/crossref_records.json` qua cleaning pipeline.
- **Phương án đã chọn:** Phương án 2 — rebuild từ raw snapshot.
- **Lý do:** Phương án 1 không idempotent (kết quả phụ thuộc vào state của corrupted data), khó đảm bảo loại bỏ hết lỗi tiêm vào. Phương án 2 đảm bảo tính idempotent: chạy bao nhiêu lần cũng cho cùng kết quả sạch, đúng thiết kế Self-healing pipeline.
- **Bằng chứng quyết định phù hợp:** Sau repair, `retrieval_hit_rate` phục hồi về đúng 1.000 (bằng baseline), quality gate PASSED, freshness SLA OK — chứng minh rebuild hoàn toàn hoạt động đúng.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `git push origin tiennguyen` báo `[rejected] non-fast-forward` — không push được lên remote.
- **Lệnh tái hiện:** `git push origin tiennguyen`
- **Nguyên nhân gốc:** Remote branch `tiennguyen` đã có commits mới (merge từ Member 1 qua main) sau khi tôi tạo commit local, khiến local branch bị diverge.
- **Cách xử lý:** Chạy `git fetch origin` → `git rebase origin/tiennguyen` → resolve conflict bằng `git checkout --ours` (giữ version local cho các file `src/` và `data/`) → `GIT_EDITOR=true git rebase --continue` → `git push origin tiennguyen`.
- **Cách xác minh sau khi sửa:** Push thành công với message `1c06e32..0562d8b tiennguyen -> tiennguyen`.
- **Điều học được:** Trong teamwork, luôn fetch và rebase trước khi push; dùng `--ours`/`--theirs` có chủ đích khi resolve conflict thay vì merge blindly.

## 7. Hiểu biết về luồng end-to-end

**Câu trả lời:**

1. **Dữ liệu từ Crossref đến vector index:** Crossref API (hoặc local snapshot `crossref_records.json`) → `parse_crossref_payload()` ra list `PaperRecord` → `build_clean_dataframe()` normalize text, tính `age_days`, tạo `text_for_embedding` → `LocalEmbeddingIndex.build()` encode bằng `all-MiniLM-L6-v2` → lưu vào ChromaDB PersistentClient với cosine similarity.

2. **Evaluation set và ground-truth doc IDs:** `build_test_set()` trích xuất câu hỏi từ DataFrame, lưu `ground_truth_doc_ids = [paper_id]`. Khi evaluate, `answer_question()` trả về `retrieved_doc_ids`; `retrieval_hit = any(doc_id in ground_truth_doc_ids for doc_id in retrieved_doc_ids)` — tức là hit nếu ít nhất 1 trong top-k kết quả chứa đúng paper. `mean_token_f1` đo overlap token giữa câu trả lời và ground truth text.

3. **Quality checks vs Freshness monitoring:** Quality checks (GX Expectations) kiểm tra **cấu trúc và tính hợp lệ** của dữ liệu tại một thời điểm (null check, unique, length bounds). Freshness monitoring kiểm tra **chiều thời gian** — tỉ lệ bài báo có `age_days > 180` ngày; nếu > 25% thì `is_fresh = False`. Hai cơ chế bổ sung cho nhau: GX phát hiện lỗi cấu trúc, Freshness phát hiện data staleness.

4. **Cùng test set cho baseline/corrupted/repaired:** Dùng cùng test set đảm bảo so sánh "apple to apple" — thay đổi metric chỉ do thay đổi chất lượng dữ liệu/index, không do câu hỏi khác nhau. Nếu dùng test set khác nhau, không thể kết luận rằng metric giảm là do corruption hay do câu hỏi khó hơn.

5. **Repair thành công dựa trên:** (a) **Artifact**: `repaired_metrics.json` tồn tại, `repaired_clean.csv` có đủ 24 dòng sạch; (b) **Metrics**: `retrieval_hit_rate` và `mean_token_f1` trở về bằng baseline; (c) **Quality gate**: GX PASSED trên repaired data; (d) **Freshness**: `is_fresh = True` sau repair.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal        | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| -------------------- | -------: | --------: | -------: | --------------------- |
| `retrieval_hit_rate` | 1.000    | 0.800     | 1.000    | Giảm 20pp khi corrupt (2/10 câu miss); phục hồi hoàn toàn sau repair |
| `mean_token_f1`      | 0.688    | 0.611     | 0.688    | Giảm ~7.7pp do title bị truncate và summary bị noise làm lệch embedding |
| `judge_accuracy`     | 0.800    | 0.600     | 0.800    | LLM judge nhận ra câu trả lời kém hơn khi data bị hỏng |
| `mean_judge_score`   | 3.6/5    | 3.2/5     | 3.6/5    | Nhất quán với judge_accuracy; phục hồi đầy đủ |
| Quality checks       | PASSED   | FAILED    | PASSED   | GX phát hiện đúng: blank summary vi phạm length expectation |
| Freshness status     | Fresh    | Fresh     | Fresh    | Stale date chỉ affect 2 rows (~9%), dưới ngưỡng 25% nên SLA vẫn OK |

### Kết luận từ số liệu

1. **[Data corruption]** tiêm 6 loại lỗi (blank summary, noise, truncate title, drop records, stale date, duplicate) → **[quality gate FAILED]** (blank summary vi phạm `ExpectColumnValueLengthsToBeBetween`) → **[hit_rate giảm từ 1.000 xuống 0.800, f1 từ 0.688 xuống 0.611]** do embedding của corrupted text không match với query embedding (Silent Failure).

2. **[Repair action]** rebuild từ `crossref_records.json` qua cleaning pipeline → **[quality gate PASSED, freshness OK]** → **[hit_rate phục hồi 1.000, f1 phục hồi 0.688]** — chứng minh idempotent repair hiệu quả.

**Corruption ảnh hưởng rõ nhất:** `blank_summary` và `inject_noise` — vì `text_for_embedding` phụ thuộc nặng vào summary. Khi summary bị xóa hoặc nhiễu, embedding vector lệch xa khỏi query vector, dẫn đến retrieval miss.

**Kết quả khác kỳ vọng:** Freshness SLA vẫn `is_fresh = True` dù có inject stale date — vì chỉ 2/20 rows (~9%) bị stale, dưới ngưỡng 25%. Điều này cho thấy Freshness SLA không đủ nhạy với corruption nhỏ; cần bổ sung metric khác (e.g. median age) để phát hiện sớm hơn.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Data pipeline:** Idempotent repair phải luôn rebuild từ nguồn raw gốc — không "vá" từ data đã corrupt, vì không thể biết hết các lỗi đã tiêm vào.
2. **Data quality/observability:** Quality Gate (GX) và Freshness SLA bổ sung cho nhau nhưng không thay thế nhau — GX phát hiện lỗi cấu trúc tức thì, Freshness phát hiện data drift theo thời gian. Cần cả hai.
3. **RAG agent:** Silent Failure là rủi ro thực sự — pipeline không throw exception nhưng answer quality giảm ngầm. Chỉ đo metric thường xuyên (hit rate, f1) mới phát hiện được; đây là lý do cần Continuous Benchmark Evaluation trong production.

### Nếu có thêm thời gian

Cải thiện test set bằng cách dùng LLM sinh câu hỏi phức tạp hơn (multi-hop, so sánh 2 paper) thay vì template cố định. Điều này sẽ làm lộ rõ hơn sự suy giảm khi data corrupt — vì câu hỏi đơn giản hiện tại cho hit_rate = 1.0 ở baseline, không đủ headroom để thấy sự khác biệt tinh tế.

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Lê Phước Tiến
**Ngày xác nhận:** 2026-09-26
