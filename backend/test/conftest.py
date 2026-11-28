import sys
from pathlib import Path

import pytest

# Make backend/ importable (ai_generator, config)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_generator import AIGenerator  # noqa: E402
from config import config  # noqa: E402  (also loads .env)


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "functional: hits the real Anthropic API (needs key + network)"
    )


@pytest.fixture
def api_key():
    signed_in = (Path.home() / ".config/anthropic/credentials").exists()
    if not config.ANTHROPIC_API_KEY and not signed_in:
        pytest.skip("no ANTHROPIC_API_KEY and not signed in (`ant auth login`)")
    return config.ANTHROPIC_API_KEY


@pytest.fixture
def generator(api_key):
    return AIGenerator(api_key, config.ANTHROPIC_MODEL)


class StubToolManager:
    """Records tool calls and returns a canned result; no ChromaDB involved."""

    def __init__(self, result="sunny 21C"):
        self.result = result
        self.calls = []

    def execute_tool(self, name, **kwargs):
        self.calls.append((name, kwargs))
        return self.result


@pytest.fixture
def tool_manager():
    return StubToolManager()


WEATHER_TOOL = {
    "name": "get_weather",
    "description": "Get the current weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}


@pytest.fixture
def tools():
    return [WEATHER_TOOL]


@pytest.fixture(scope="session")
def rag(tmp_path_factory):
    """RAGSystem over a throwaway ChromaDB built from ../docs (local embeddings, no API)."""
    import dataclasses

    from rag_system import RAGSystem

    cfg = dataclasses.replace(
        config, CHROMA_PATH=str(tmp_path_factory.mktemp("chroma"))
    )
    system = RAGSystem(cfg)
    docs = Path(__file__).resolve().parent.parent.parent / "docs"
    courses, _ = system.add_course_folder(str(docs))
    assert courses > 0, "no course docs ingested"
    return system


# ---------------------------------------------------------------------------
# API test fixtures (no ChromaDB, no Anthropic, no static files)
# ---------------------------------------------------------------------------
from unittest.mock import MagicMock  # noqa: E402

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from typing import List, Optional  # noqa: E402


@pytest.fixture
def sample_sources():
    return [
        {"text": "MCP Course - Lesson 1", "url": "https://example.com/mcp/1"},
        {"text": "MCP Course - Lesson 2", "url": None},
    ]


@pytest.fixture
def mock_rag_system(sample_sources):
    """A RAGSystem stand-in with canned answers; override per test as needed."""
    rag_mock = MagicMock()
    rag_mock.query.return_value = ("Test answer", sample_sources)
    rag_mock.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["MCP Course", "Chroma Course"],
    }
    rag_mock.session_manager.create_session.return_value = "session_1"
    return rag_mock


def build_test_app(rag_system) -> FastAPI:
    """Mirror of the endpoints in app.py, minus static mounting and startup ingestion.

    app.py cannot be imported in tests: it builds a real RAGSystem and mounts
    ../frontend. The models/routes here must be kept in sync with app.py.
    """
    app = FastAPI(title="Course Materials RAG System (test)")

    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class Source(BaseModel):
        text: str
        url: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[Source]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id or rag_system.session_manager.create_session()
            answer, sources = rag_system.query(request.query, session_id)
            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/session/{session_id}")
    async def delete_session(session_id: str):
        rag_system.session_manager.clear_session(session_id)
        return {"status": "ok"}

    @app.get("/")
    async def root():
        return {"message": "Course Materials RAG System"}

    return app


@pytest.fixture
def client(mock_rag_system):
    return TestClient(build_test_app(mock_rag_system))
