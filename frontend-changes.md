# Frontend / Dev Workflow Changes: Code Quality Tooling

Note: the requested feature (black formatting + quality scripts) is dev tooling, not a UI feature.
**No files under `frontend/` were modified.** black only formats Python, so no frontend formatter was added.

## Changes
- `pyproject.toml`: added `black>=25.1.0` to the `dev` dependency group and a `[tool.black]` config
  (line length 88, py313, excludes `chroma_db`, `.venv`, `.trees`). `uv.lock` updated.
- `scripts/format.sh`: auto-formats `backend/` and `main.py` with black.
- `scripts/check.sh`: runs `black --check` then the offline tests (`pytest -m "not functional"`); exits non-zero on failure.
- Reformatted 13 Python files in `backend/` with black (whitespace/style only; offline tests pass: 23 passed).

## Usage
```bash
./scripts/format.sh   # format
./scripts/check.sh    # verify formatting + tests
```
---

# Frontend changes

No frontend files (`frontend/`) were changed. This feature is test infrastructure only:

- `backend/test/test_api.py` — new offline tests for `/`, `/api/query`, `/api/courses`, `/api/session/{id}`. These are the endpoints the frontend `script.js` calls, so they pin the request/response contract (`answer`, `sources[{text,url}]`, `session_id`, `total_courses`, `course_titles`).
- `backend/test/conftest.py` — added shared fixtures: `mock_rag_system`, `sample_sources`, `client`, and `build_test_app()`. The test app defines the endpoints inline, so the real `app.py` is never imported (it mounts `../frontend` and builds a real `RAGSystem`). Keep it in sync with `app.py`.
- `pyproject.toml` — added `[tool.pytest.ini_options]` (`testpaths`, `pythonpath`, `addopts`, `functional` marker). `pytest` now works from the repo root or `backend/`.

Run offline: `uv run pytest -m "not functional"`.
