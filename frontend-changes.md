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
