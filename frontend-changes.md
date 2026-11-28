# Frontend changes

No frontend files (`frontend/`) were changed. This feature is test infrastructure only:

- `backend/test/test_api.py` — new offline tests for `/`, `/api/query`, `/api/courses`, `/api/session/{id}`. These are the endpoints the frontend `script.js` calls, so they pin the request/response contract (`answer`, `sources[{text,url}]`, `session_id`, `total_courses`, `course_titles`).
- `backend/test/conftest.py` — added shared fixtures: `mock_rag_system`, `sample_sources`, `client`, and `build_test_app()`. The test app defines the endpoints inline, so the real `app.py` is never imported (it mounts `../frontend` and builds a real `RAGSystem`). Keep it in sync with `app.py`.
- `pyproject.toml` — added `[tool.pytest.ini_options]` (`testpaths`, `pythonpath`, `addopts`, `functional` marker). `pytest` now works from the repo root or `backend/`.

Run offline: `uv run pytest -m "not functional"`.
