# Phase 1 Baseline Report

> Generated: 2026-09-26T05:30:30.097603+00:00

---

## 1. Data Source Summary

| Field | Value |
|---|---|
| Source API | Crossref REST API |
| Query | `agentic retrieval augmented generation large language model` |
| Raw records fetched | 24 |
| Clean records | 24 |

---

## 2. Baseline Evaluation Metrics

| Metric | Value |
|---|---|
| Retrieval Hit Rate | 100.0% |
| Mean Token F1      | 68.8% |
| Judge Accuracy     | 80.0% |
| Mean Judge Score   | 3.600 / 5 |
| Samples evaluated  | 10 |

---

## 3. Data Quality Gate (Great Expectations)

**Overall status:** ✅ PASSED

```json
{'report_name': 'baseline_quality_report', 'success': True, 'total_records': 24, 'evaluated_expectations': 7, 'successful_expectations': 7, 'failed_expectations': 0, 'details': {'success': True, 'results': [{'success': True, 'expectation_config': {'type': 'expect_table_row_count_to_be_between', 'kwargs': {'batch_id': 'papers_source_baseline_quality_report-papers_asset_baseline_quality_report', 'min_value': 10, 'max_value': 100}, 'meta': {}, 'id': '17ce8f90-78f4-4701-87c3-6cd57d9929a0', 'severity': 'critical'}, 'result': {'observed_value': 24}, 'meta': {}, 'exception_info': {'raised_exception': False, 'exception_traceback': None, 'exception_message': None}}, {'success': True, 'expectation_config': {'type': 'expect_column_values_to_not_be_null', 'kwargs': {'batch_id': 'papers_source_baseline_quality_report-papers_asset_baseline_quality_report', 'column': 'paper_id'}, 'meta': {}, 'id': '5c520223-be76-4c52-820e-c8ce87976cbe', 'severity': 'critical'}, 'result': {'element_count': 24, 'unexpected_count': 0, 'unexpected_percent': 0.0, 'partial_unexpected_list': [], 'partial_unexpected_counts': [], 'partial_unexpected_index_list': []}, 'meta': {}, 'exception_info': {'raised_exception': False, 'exception_traceback': None, 'exception_message': None}}, {'success': True, 'expectation_config': {'type': 'expect_column_values_to_be_unique', 'kwargs': {'batch_id': 'papers_source_baseline_quality_report-papers_asset_baseline_quality_report', 'column': 'paper_id'}, 'meta': {}, 'id': '90343d71-1f80-4712-aaa1-d9777830a2d9', 'severity': 'critical'}, 'result': {'element_count': 24, 'unexpected_count': 0, 'unexpected_percent': 0.0, 'partial_unexpected_list': [], 'missing_count': 0, 'missing_percent': 0.0, 'unexpected_percent_total': 0.0, 'unexpected_percent_nonmissing': 0.0, 'partial_unexpected_counts': [], 'partial_unexpected_index_list': []}, 'meta': {}, 'exception_info': {'raised_exception': False, 'exception_traceback': None, 'exception_message': None}}, {'success': True, 'expectation_config': {'type': 'expect_column_values_to_not_be_null', 'kwargs': {'batch_id': 'papers_source_baseline_quality_report-papers_asset_baseline_quality_report', 'column': 'title'}, 'meta': {}, 'id': '5d30674e-ebe7-42ec-9ee5-76e012e30786', 'severity': 'critical'}, 'result': {'element_count': 24, 'unexpected_count': 0, 'unexpected_percent': 0.0, 'partial_unexpected_list': [], 'partial_unexpected_counts': [], 'partial_unexpected_index_list': []}, 'meta': {}, 'exception_info': {'raised_exception': False, 'exception_traceback': None, 'exception_message': None}}, {'success': True, 'expectation_config': {'type': 'expect_column_value_lengths_to_be_between', 'kwargs': {'batch_id': 'papers_source_baseline_quality_report-papers_asset_baseline_quality_report', 'column': 'title', 'min_value': 8, 'max_value': 500}, 'meta': {}, 'id': 'eb00e599-7fd7-48c7-a00e-9061592563e9', 'severity': 'critical'}, 'result': {'element_count': 24, 'unexpected_count': 0, 'unexpected_percent': 0.0, 'partial_unexpected_list': [], 'missing_count': 0, 'missing_percent': 0.0, 'unexpected_percent_total': 0.0, 'unexpected_percent_nonmissing': 0.0, 'partial_unexpected_counts': [], 'partial_unexpected_index_list': []}, 'meta': {}, 'exception_info': {'raised_exception': False, 'exception_traceback': None, 'exception_message': None}}, {'success': True, 'expectation_config': {'type': 'expect_column_values_to_not_be_null', 'kwargs': {'batch_id': 'papers_source_baseline_quality_report-papers_asset_baseline_quality_report', 'column': 'text_for_embedding'}, 'meta': {}, 'id': '3536add3-5fc9-4122-90c5-c88fb117d54a', 'severity': 'critical'}, 'result': {'element_count': 24, 'unexpected_count': 0, 'unexpected_percent': 0.0, 'partial_unexpected_list': [], 'partial_unexpected_counts': [], 'partial_unexpected_index_list': []}, 'meta': {}, 'exception_info': {'raised_exception': False, 'exception_traceback': None, 'exception_message': None}}, {'success': True, 'expectation_config': {'type': 'expect_column_value_lengths_to_be_between', 'kwargs': {'batch_id': 'papers_source_baseline_quality_report-papers_asset_baseline_quality_report', 'column': 'summary', 'min_value': 20, 'max_value': 5000}, 'meta': {}, 'id': '9e4a263b-e03f-4dc4-a8aa-17b56c8f9055', 'severity': 'critical'}, 'result': {'element_count': 24, 'unexpected_count': 0, 'unexpected_percent': 0.0, 'partial_unexpected_list': [], 'missing_count': 0, 'missing_percent': 0.0, 'unexpected_percent_total': 0.0, 'unexpected_percent_nonmissing': 0.0, 'partial_unexpected_counts': [], 'partial_unexpected_index_list': []}, 'meta': {}, 'exception_info': {'raised_exception': False, 'exception_traceback': None, 'exception_message': None}}], 'suite_name': 'papers_suite_baseline_quality_report', 'suite_parameters': {}, 'statistics': {'evaluated_expectations': 7, 'successful_expectations': 7, 'unsuccessful_expectations': 0, 'success_percent': 100.0}, 'meta': {'great_expectations_version': '1.23.2', 'batch_spec': {'batch_data': 'PandasDataFrame'}, 'batch_markers': {'ge_load_time': '20260926T053054.202652Z', 'pandas_data_fingerprint': '7ba7fdea7ec3c00f015df4d8e261dd8c'}, 'active_batch_definition': {'datasource_name': 'papers_source_baseline_quality_report', 'data_connector_name': 'fluent', 'data_asset_name': 'papers_asset_baseline_quality_report', 'batch_identifiers': {'dataframe': '<DATAFRAME>'}}}, 'id': None}}
```

---

## 4. Freshness SLA

| Field | Value |
|---|---|
| Is Fresh            | ✅ Yes |
| Latest Published    | 2026-07-22 |
| Oldest Published    | 2026-03-28 |
| Stale Rows (>180d)  | 1 / 24 |
| Stale Ratio         | 4.2% |

---

_End of Phase 1 Report_
