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
---

# Frontend changes: dark/light theme toggle

- `frontend/index.html`: added a fixed top-right `#themeToggle` button with inline sun and moon SVG icons. It has `aria-label` and `aria-pressed`, and it is a real `<button>`, so it works with the keyboard. A small inline script in `<head>` applies the saved theme before first paint to avoid a flash. Cache-busting versions were bumped.
- `frontend/style.css`:
  - Added a `[data-theme="light"]` variable set that overrides the dark defaults.
  - Added `--code-bg`, `--link-color` and `--link-hover` variables in place of hard-coded colors.
  - Added `.theme-toggle` styles: round, matches the surface/border look, hover scale, and a `:focus-visible` ring.
  - The sun and moon icons cross-fade and rotate. Background, text and border colors transition over 0.3s.
- `frontend/script.js`: added `setupThemeToggle()`. It flips `data-theme` on `<html>`, saves the choice to `localStorage` (default is dark), and updates the ARIA state.

# Light theme CSS variables

The `[data-theme="light"]` block in `frontend/style.css` now defines the full light palette:

- **Backgrounds and surfaces:** `--background` #f8fafc, `--surface` #ffffff, `--surface-hover` #e2e8f0, `--assistant-message` #e2e8f0, `--welcome-bg` #dbeafe.
- **Text:** `--text-primary` #0f172a (about 17:1 on the background) and `--text-secondary` #475569 (about 7:1 on the background, about 6.1:1 on hover surfaces).
- **Primary colors:** darkened to `--primary-color`, `--user-message` and `--welcome-border` #1d4ed8, and `--primary-hover` #1e40af. Primary text on white is 6.7:1, and white text on user messages is 6.7:1. Both meet WCAG AA (4.5:1).
- **Borders and focus:** `--border-color` #cbd5e1 and `--focus-ring` at higher opacity.
- **Shadows, code and links:** added `--shadow-lg` (the hard-coded dark shadow was replaced with it) and `--code-bg`. Link colors are `--link-color` and `--link-hover`: #1d4ed8 and #1e40af.
- Ratios were computed with the WCAG relative-luminance formula.
