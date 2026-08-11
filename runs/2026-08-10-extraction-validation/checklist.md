# Extraction validation checklist — p01 and p02

*Owner task. This is the M1 precondition and Done condition that has not yet
been met: `tasks/02-milestone-1.md` requires the owner to re-check record
fields **as facts in the repo** — *this artifact exists at this path, these
numbers appear in this file* — never as review verdicts. Your own peer-review
text stays out of this entirely.*

## What this is not

The schema review already done (which produced the eleven items in
`docs/deferred-to-m2.md`) asked a different question: **can the schema express
what is true?** This asks: **did the extractor record what is actually there?**
A record could be systematically wrong in a way no amount of schema discussion
surfaces — if `monitoring_chart_count` said 6 when the dashboard has 8, every
conversation this session would have gone the same way.

## How to use it

For each row: open the cited path in the clone and answer **does the file say
this?** — yes / no / can't tell. Nothing more. Clones are at `clones/p01` and
`clones/p02`, pinned at the commits below.

**⚑ marks the high-leverage rows** — the ones where an error would most change
what M1 concludes. If time is short, do those and stop; partial validation with
a stated stopping point is worth more than none.

---

## p01 — commit `42cda614c65c970bc1b5ca9b25f4252baef233e7`

- [ ] **`knowledge_base_present`** = `present`  
      `src/ingestion/run.py:96-105`, `src/ingestion/qdrant_index.py:16-32`, `src/search/dense.py:17-23`
- [ ] **`llm_in_flow`** = `present`  
      `src/api/routes.py:70-76`, `src/api/answer.py:46-52`
- [ ] **`retrieval_flow`** = `kb_and_llm`  
      `src/api/routes.py:52-55`, `src/api/routes.py:70-76`
- [ ] ⚑ **`problem_statement`** = `specific`  
      `README.md:62-64`
- [ ] ⚑ **`interface_kind`** = `web_ui`  
      `src/api/static/index.html:477`, `src/api/app.py:18`, `src/api/app.py:67-69`
- [ ] **`interface_evidence_kind`** = `code_and_screenshot`  
      `screenshots/chat-ui.png`, `README.md:41-43`
- [ ] ⚑ **`ingestion_kind`** = `script_or_notebook`  
      `src/ingestion/run.py:29-37`, `src/ingestion/run.py:118-119`, `docs/architecture.md:87-88`
- [ ] **`ingestion_single_command`** = `True`  
      `README.md:22`, `docs/architecture.md:96-98`
- [ ] **`ingestion_output_stated`** = `True`  
      `docs/architecture.md:108`, `src/ingestion/run.py:115-117`
- [ ] **`retrieval_eval_present`** = `True`  
      `docs/evaluation.md:3-10`, `notebooks/01_retrieval_evaluation.py:52-89`
- [ ] ⚑ **`retrieval_eval_approaches_compared`** = `4`  
      `docs/evaluation.md:7-10`, `notebooks/01_retrieval_evaluation.py:55`
- [ ] **`retrieval_eval_set_committed`** = `committed`  
      `src/evaluation/test_set.py:1-137`
- [ ] ⚑ **`retrieval_eval_set_size`** = `27`  
      `src/evaluation/test_set.py:1-137`, `docs/evaluation.md:19`
- [ ] ⚑ **`retrieval_eval_relevance_rule`** = `source_level`  
      `notebooks/01_retrieval_evaluation.py:41-49`, `src/evaluation/test_set.py:5`, `src/ingestion/wikipedia.py:67`
- [ ] **`retrieval_eval_config_matches_shipped`** = `differs`  
      `notebooks/01_retrieval_evaluation.py:65-69`, `src/api/routes.py:40-55`, `src/ingestion/embedding.py:25-29`, `src/api/routes.py:17-19`
- [ ] **`retrieval_eval_uncertainty_stated`** = `False`  
      `docs/evaluation.md:1-19`
- [ ] ⚑ **`retrieval_best_approach_shipped`** = `mixed_result`  
      `docs/evaluation.md:9-10`, `src/api/routes.py:54-55`
- [ ] **`llm_eval_present`** = `True`  
      `docs/evaluation.md:12-19`, `notebooks/02_llm_evaluation.py:63-98`
- [ ] ⚑ **`llm_eval_approaches_compared`** = `1`  
      `docs/evaluation.md:14-17`, `notebooks/02_llm_evaluation.py:37-48`
- [ ] **`llm_eval_judge_kind`** = `model_judge`  
      `notebooks/02_llm_evaluation.py:65-85`, `docs/evaluation.md:19`
- [ ] **`llm_eval_judge_spotchecked`** = `False`  
      `notebooks/02_llm_evaluation.py:91-121`, `docs/evaluation.md:12-19`
- [ ] **`llm_eval_question_generator`** = `none_committed`  
      `src/evaluation/test_set.py:1-137`
- [ ] ⚑ **`llm_eval_metric_at_ceiling`** = `True`  
      `docs/evaluation.md:17`, `notebooks/02_llm_evaluation.py:66-68`
- [ ] **`llm_eval_role_overlap`** = `same_family`  
      `notebooks/02_llm_evaluation.py:44`, `notebooks/02_llm_evaluation.py:64-88`, `src/evaluation/test_set.py:1-137`
- [ ] **`llm_eval_config_matches_shipped`** = `differs`  
      `notebooks/02_llm_evaluation.py:37-46`, `src/api/routes.py:36-55`
- [ ] ⚑ **`monitoring_kind`** = `feedback_and_dashboard`  
      `src/api/routes.py:161-172`, `src/api/static/index.html:409-434`, `dashboards/food-wine-dashboard.json`
- [ ] **`monitoring_dashboard_provenance`** = `committed_definitions`  
      `dashboards/food-wine-dashboard.json`, `dashboards/grafana-dashboard.yml`, `dashboards/grafana-datasource.yml`, `docker-compose.yml`
- [ ] **`monitoring_instrumentation`** = `traced_on_request_path`  
      `src/api/routes.py:37-95`, `src/api/db.py:45-61`
- [ ] ⚑ **`monitoring_chart_count`** = `8`  
      `dashboards/food-wine-dashboard.json`, `docs/monitoring.md:5-14`
- [ ] **`monitoring_charts_bound_to_data`** = `all`  
      `dashboards/food-wine-dashboard.json`, `docker/init-db.sql:1-18`, `src/api/db.py:41-58`
- [ ] ⚑ **`containerization_kind`** = `compose_full`  
      `docker-compose.yml:1-24`, `docker/Dockerfile:1-23`
- [ ] ⚑ **`run_instructions`** = `complete`  
      `README.md:9-26`, `.env.example:1-5`
- [ ] **`run_instructions_gap_count`** = `3`  
      `README.md:19-22`, `src/api/app.py:29-51`, `src/search/bm25.py:23-26`, `deploy/deploy.sh:14`, `docs/deployment.md:9`, `docs/deployment.md:13-27`
- [ ] ⚑ **`dependency_versions_pinned`** = `lockfile_committed`  
      `uv.lock:1-3`, `pyproject.toml:7-23`, `docker/Dockerfile:11-14`
- [ ] ⚑ **`data_accessible`** = `automated_or_committed`  
      `data/data-03-00009-s001.zip`, `src/ingestion/mdpi.py:10-11`, `src/ingestion/wikipedia.py:46-51`, `src/ingestion/infovini.py:9-12`
- **`hybrid_search`**
- [ ] **`hybrid_search.present`** = `True`  
      `src/search/hybrid.py:6-51`
- [ ] **`hybrid_search.shipped_enabled`** = `True`  
      `src/api/routes.py:52-54`
- [ ] **`hybrid_search.evaluated`** = `True`  
      `docs/evaluation.md:7-10`, `notebooks/01_retrieval_evaluation.py:68`
- [ ] **`hybrid_search.measured_effect`** = `improves`  
      `docs/evaluation.md:7-9`
- [ ] **`hybrid_search.decision_documented`** = `False`  
      `docs/evaluation.md:3-19`, `docs/architecture.md:80-92`
- [ ] **`hybrid_search.decision_axes`** = `[]`  
      `docs/evaluation.md:3-19`
- **`reranking`**
- [ ] **`reranking.present`** = `True`  
      `src/search/reranker.py:18-45`
- [ ] **`reranking.shipped_enabled`** = `True`  
      `src/api/routes.py:55`
- [ ] **`reranking.evaluated`** = `True`  
      `docs/evaluation.md:10`, `notebooks/01_retrieval_evaluation.py:69`
- [ ] **`reranking.measured_effect`** = `mixed`  
      `docs/evaluation.md:9-10`
- [ ] **`reranking.decision_documented`** = `False`  
      `docs/evaluation.md:9-10`, `docs/architecture.md:45-53`, `docs/limitations.md:10`
- [ ] **`reranking.decision_axes`** = `[]`  
      `docs/evaluation.md:3-19`
- **`query_rewriting`**
- [ ] **`query_rewriting.present`** = `True`  
      `src/search/query_rewriter.py:16-42`
- [ ] **`query_rewriting.shipped_enabled`** = `True`  
      `src/api/routes.py:40`
- [ ] **`query_rewriting.evaluated`** = `False`  
      `notebooks/01_retrieval_evaluation.py:57-69`, `notebooks/02_llm_evaluation.py:38-43`
- [ ] **`query_rewriting.measured_effect`** = `not_measured`  
      `docs/evaluation.md:5-17`
- [ ] **`query_rewriting.decision_documented`** = `False`  
      `docs/evaluation.md:3-19`, `docs/architecture.md:80-92`
- [ ] **`query_rewriting.decision_axes`** = `[]`  
      `docs/evaluation.md:3-19`
- [ ] ⚑ **`cloud_deployment`** = `deployment_code_committed`  
      `deploy/provision.sh:12-25`, `deploy/deploy.sh:13-25`, `docker/Caddyfile:1-7`, `docker-compose.yml:67-76`
- [ ] **`headline_numbers_traceable`** = `some_traceable`  
      `screenshots/ingestion.png`, `docs/architecture.md:108`, `src/evaluation/test_set.py:1-137`, `dashboards/food-wine-dashboard.json`, `docs/evaluation.md:5-17`, `notebooks/01_retrieval_evaluation.py:1-9`, `notebooks/02_llm_evaluation.py:1-12`
- [ ] ⚑ **`untraceable_number_count`** = `18`  
      `docs/evaluation.md:7-10`, `docs/evaluation.md:16-17`, `notebooks/01_retrieval_evaluation.py:1-9`, `notebooks/02_llm_evaluation.py:1-12`
- [ ] ⚑ **`document_code_conflicts`** = `1`  
      `docs/evaluation.md:9`, `notebooks/01_retrieval_evaluation.py:41-49`, `src/evaluation/test_set.py:1-137`, `src/ingestion/wikipedia.py:67`
- [ ] **`broken_reference_count`** = `0`  
      `README.md:45-60`
- [ ] **`document_number_conflicts`** = `2`  
      `README.md:79`, `docs/architecture.md:68`, `docs/limitations.md:6`, `screenshots/grafana.png`
- [ ] **`limitations_section`** = `includes_structural`  
      `docs/limitations.md:10`, `docs/limitations.md:11-12`
- [ ] **`artifact_reference_strength`** = `all_referenced`  
      `docs/evaluation.md:19`, `README.md:52-53`, `docs/monitoring.md:3`, `README.md:22`, `docs/deployment.md:39-40`
- [ ] **`artifacts_unreferenced_count`** = `0`  
      `docs/evaluation.md:19`, `README.md:52-53`, `docs/monitoring.md:3`, `README.md:22`, `docs/deployment.md:39-40`
- [ ] **`corpus_language`** = `portuguese`  
      `src/ingestion/mdpi.py:96`, `src/ingestion/infovini.py:146`, `src/ingestion/wikipedia.py:47-50`
- [ ] **`corpus_domain`** = `food_and_wine`  
      `docs/architecture.md:73-78`, `README.md:62-64`
- [ ] **`interface_framework`** = `flask`  
      `src/api/app.py:4`, `src/api/app.py:18`, `pyproject.toml:8`
- [ ] **`vector_store`** = `qdrant`  
      `src/search/dense.py:4-14`, `docker-compose.yml:26-31`
- [ ] **`llm_provider`** = `openai`  
      `src/api/answer.py:4`, `src/search/query_rewriter.py:4`, `.env.example:1-6`
- [ ] **`repo_file_count`** = `53`  
      `<repo>`

---

## p02 — commit `7e603cbee11af5aef92d242ed70f51c797bfd909`

- [ ] **`knowledge_base_present`** = `present`  
      `src/rag.py:65-71`, `src/ingest.py:24-32`
- [ ] **`llm_in_flow`** = `present`  
      `src/rag.py:117-124`
- [ ] **`retrieval_flow`** = `kb_and_llm`  
      `src/serve.py:50-58`, `src/rag.py:99-124`
- [ ] ⚑ **`problem_statement`** = `specific`  
      `README.md:5-10`
- [ ] ⚑ **`interface_kind`** = `web_ui`  
      `src/app.py:1-9`, `docker-compose.yaml:49-60`
- [ ] **`interface_evidence_kind`** = `code_only`  
      `README.md:117-135`
- [ ] ⚑ **`ingestion_kind`** = `script_or_notebook`  
      `src/ingest.py:144-145`, `src/ingest_json.py:95-98`
- [ ] **`ingestion_single_command`** = `True`  
      `README.md:75-77`
- [ ] **`ingestion_output_stated`** = `False`  
      `README.md:68-91`, `src/ingest.py:140-141`
- [ ] **`retrieval_eval_present`** = `True`  
      `notebooks/rag.ipynb:cell7`, `notebooks/rag.ipynb:cell8`, `README.md:144-171`
- [ ] ⚑ **`retrieval_eval_approaches_compared`** = `2`  
      `notebooks/rag.ipynb:cell8`, `notebooks/rag.ipynb:cell12`
- [ ] **`retrieval_eval_set_committed`** = `committed`  
      `data/ground_truth_dataset.csv`, `notebooks/rag.ipynb:cell6`
- [ ] ⚑ **`retrieval_eval_set_size`** = `997`  
      `data/ground_truth_dataset.csv`, `notebooks/rag.ipynb:cell7`
- [ ] ⚑ **`retrieval_eval_relevance_rule`** = `document_level`  
      `notebooks/rag.ipynb:cell7`, `notebooks/ground_truth.ipynb:cell1`
- [ ] **`retrieval_eval_config_matches_shipped`** = `differs`  
      `notebooks/rag.ipynb:cell2`, `src/ingest.py:94-113`, `src/ingest_json.py:66-84`, `notebooks/rag.ipynb:cell7`, `src/rag.py:57-71`
- [ ] **`retrieval_eval_uncertainty_stated`** = `False`  
      `README.md:151-171`, `notebooks/rag.ipynb:cell8`, `notebooks/rag.ipynb:cell12`
- [ ] ⚑ **`retrieval_best_approach_shipped`** = `mixed_result`  
      `notebooks/rag.ipynb:cell8`, `notebooks/rag.ipynb:cell12`, `README.md:166-170`
- [ ] **`llm_eval_present`** = `True`  
      `notebooks/rag.ipynb:cell17`, `notebooks/rag.ipynb:cell19`, `README.md:175-186`
- [ ] ⚑ **`llm_eval_approaches_compared`** = `2`  
      `notebooks/rag.ipynb:cell16`, `notebooks/rag.ipynb:cell24`, `README.md:179-183`
- [ ] **`llm_eval_judge_kind`** = `model_judge`  
      `notebooks/rag.ipynb:cell17`, `notebooks/rag.ipynb:cell19`
- [ ] **`llm_eval_judge_spotchecked`** = `False`  
      `notebooks/rag.ipynb:cell17`, `notebooks/rag.ipynb:cell20`, `data/rag_results_for_eval_gemini-2.5-flash-lite.json`
- [ ] **`llm_eval_question_generator`** = `generator_ties_question_to_passage`  
      `notebooks/ground_truth.ipynb:cell0`, `notebooks/ground_truth.ipynb:cell1`
- [ ] ⚑ **`llm_eval_metric_at_ceiling`** = `False`  
      `notebooks/rag.ipynb:cell18`, `notebooks/rag.ipynb:cell20`, `notebooks/rag.ipynb:cell25`, `notebooks/rag.ipynb:cell26`
- [ ] **`llm_eval_role_overlap`** = `same_model`  
      `notebooks/ground_truth.ipynb:cell0`, `notebooks/rag.ipynb:cell16,cell17,cell19`
- [ ] **`llm_eval_config_matches_shipped`** = `differs`  
      `notebooks/rag.ipynb:cell15`, `src/rag.py:117-137`
- [ ] ⚑ **`monitoring_kind`** = `dashboard_only`  
      `src/serve.py:8-14`, `src/rag.py:12-16`, `src/rag.py:58-61`, `docker-compose.yaml:37-47`, `README.md:191-195`
- [ ] **`monitoring_dashboard_provenance`** = `stock_tool_ui`  
      `docker-compose.yaml:38-47`, `README.md:36`, `README.md:193-195`
- [ ] **`monitoring_instrumentation`** = `traced_on_request_path`  
      `src/rag.py:12-16`, `src/rag.py:58-61`, `src/rag.py:87-88`, `src/serve.py:8-14`
- [ ] ⚑ **`monitoring_chart_count`** = `None`  
      `docker-compose.yaml:38-47`, `README.md:191-195`
- [ ] **`monitoring_charts_bound_to_data`** = `not_applicable`  
      `docker-compose.yaml:38-47`
- [ ] ⚑ **`containerization_kind`** = `compose_full`  
      `docker-compose.yaml:7-60`, `Dockerfile:1-26`, `Dockerfile.ui:1-26`
- [ ] ⚑ **`run_instructions`** = `complete`  
      `README.md:42-55`, `README.md:59-65`, `README.md:97-114`
- [ ] **`run_instructions_gap_count`** = `4`  
      `README.md:99-104`, `src/rag.py:46-49`, `README.md:121-124`, `docker-compose.yaml:24-26`, `README.md:59-65`, `docker-compose.yaml:9-19`, `README.md:88-89`, `src/ingest_json.py:96-98`
- [ ] ⚑ **`dependency_versions_pinned`** = `lockfile_committed`  
      `uv.lock`, `pyproject.toml:7-26`, `Dockerfile:14-17`
- [ ] ⚑ **`data_accessible`** = `automated_or_committed`  
      `README.md:72-77`, `src/ingest.py:47-52`, `data/ground_truth_dataset.csv`
- **`hybrid_search`**
- [ ] **`hybrid_search.present`** = `False`  
      `src/rag.py:65-71`, `src/ingest.py:24-32`
- [ ] **`hybrid_search.shipped_enabled`** = `False`  
      `src/rag.py:65-71`
- [ ] **`hybrid_search.evaluated`** = `False`  
      `notebooks/rag.ipynb:cell8`, `notebooks/rag.ipynb:cell12`
- [ ] **`hybrid_search.measured_effect`** = `not_measured`  
      `notebooks/rag.ipynb:cell8`, `notebooks/rag.ipynb:cell12`
- [ ] **`hybrid_search.decision_documented`** = `False`  
      `README.md`
- [ ] **`hybrid_search.decision_axes`** = `[]`  
      `README.md`
- **`reranking`**
- [ ] **`reranking.present`** = `True`  
      `notebooks/rag.ipynb:cell10`, `notebooks/test.ipynb:cell22`
- [ ] **`reranking.shipped_enabled`** = `False`  
      `src/rag.py:57-71`, `Dockerfile:20`
- [ ] **`reranking.evaluated`** = `True`  
      `notebooks/rag.ipynb:cell12`
- [ ] **`reranking.measured_effect`** = `mixed`  
      `notebooks/rag.ipynb:cell8`, `notebooks/rag.ipynb:cell12`, `README.md:166-170`
- [ ] **`reranking.decision_documented`** = `True`  
      `README.md:166-170`
- [ ] **`reranking.decision_axes`** = `['mrr', 'hit_rate', 'latency']`  
      `README.md:166-170`
- **`query_rewriting`**
- [ ] **`query_rewriting.present`** = `False`  
      `src/rag.py:54-71`, `notebooks/rag.ipynb:cell15`
- [ ] **`query_rewriting.shipped_enabled`** = `False`  
      `src/rag.py:54-63`
- [ ] **`query_rewriting.evaluated`** = `False`  
      `notebooks/rag.ipynb:cell8`, `notebooks/rag.ipynb:cell12`
- [ ] **`query_rewriting.measured_effect`** = `not_measured`  
      `notebooks/rag.ipynb:cell8`
- [ ] **`query_rewriting.decision_documented`** = `False`  
      `README.md`
- [ ] **`query_rewriting.decision_axes`** = `[]`  
      `README.md`
- [ ] ⚑ **`cloud_deployment`** = `none`  
      `README.md:95-114`, `docker-compose.yaml:7-60`
- [ ] **`headline_numbers_traceable`** = `some_traceable`  
      `README.md:153-159`, `notebooks/rag.ipynb:cell8`, `README.md:169`, `notebooks/rag.ipynb:cell12`, `README.md:179-183`, `notebooks/rag.ipynb:cell18`, `notebooks/rag.ipynb:cell20`, `notebooks/rag.ipynb:cell25`, `notebooks/rag.ipynb:cell26`, `README.md:170`, `README.md:186`
- [ ] ⚑ **`untraceable_number_count`** = `2`  
      `README.md:170`, `README.md:186`
- [ ] ⚑ **`document_code_conflicts`** = `1`  
      `README.md:181-182`, `notebooks/rag.ipynb:cell17,cell19`, `data/rag_results_for_eval_gemini-2.5-flash-lite.json`
- [ ] **`broken_reference_count`** = `5`  
      `README.md:202-228`
- [ ] **`document_number_conflicts`** = `1`  
      `README.md:121`, `README.md:124`, `README.md:134`, `docker-compose.yaml:26`, `Dockerfile:23`
- [ ] **`limitations_section`** = `absent`  
      `README.md:1-234`
- [ ] **`artifact_reference_strength`** = `all_referenced`  
      `README.md:25`, `README.md:202-228`
- [ ] **`artifacts_unreferenced_count`** = `0`  
      `README.md:202-228`
- [ ] **`corpus_language`** = `english`  
      `data/ground_truth_dataset.csv`, `data/rag_results_for_eval_gemini-2.5-flash-lite.json`
- [ ] **`corpus_domain`** = `physics_preprint_abstracts`  
      `README.md:19-23`, `src/ingest.py:16`
- [ ] **`interface_framework`** = `streamlit`  
      `src/app.py:1-9`, `Dockerfile.ui:26`
- [ ] **`vector_store`** = `qdrant`  
      `src/rag.py:42`, `docker-compose.yaml:9-19`
- [ ] **`llm_provider`** = `google_gemini`  
      `src/rag.py:22`, `src/rag.py:50`
- [ ] **`repo_file_count`** = `22`  
      `<repo>`
