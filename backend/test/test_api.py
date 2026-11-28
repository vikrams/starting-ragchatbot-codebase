"""Offline tests for the FastAPI endpoints, using the test app from conftest."""
import pytest


class TestRoot:
    def test_root_ok(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "message" in r.json()


class TestQueryEndpoint:
    def test_creates_session_when_missing(self, client, mock_rag_system):
        r = client.post("/api/query", json={"query": "What is MCP?"})
        assert r.status_code == 200
        body = r.json()
        assert body["answer"] == "Test answer"
        assert body["session_id"] == "session_1"
        assert body["sources"][0] == {
            "text": "MCP Course - Lesson 1", "url": "https://example.com/mcp/1"}
        assert body["sources"][1]["url"] is None
        mock_rag_system.session_manager.create_session.assert_called_once()
        mock_rag_system.query.assert_called_once_with("What is MCP?", "session_1")

    def test_reuses_provided_session(self, client, mock_rag_system):
        r = client.post("/api/query", json={"query": "hi", "session_id": "session_9"})
        assert r.json()["session_id"] == "session_9"
        mock_rag_system.session_manager.create_session.assert_not_called()
        mock_rag_system.query.assert_called_once_with("hi", "session_9")

    def test_empty_sources(self, client, mock_rag_system):
        mock_rag_system.query.return_value = ("No search needed", [])
        r = client.post("/api/query", json={"query": "hello"})
        assert r.status_code == 200
        assert r.json()["sources"] == []

    @pytest.mark.parametrize("payload", [{}, {"session_id": "s"}, {"query": 123}])
    def test_invalid_payload_422(self, client, payload):
        assert client.post("/api/query", json=payload).status_code == 422

    def test_malformed_json_422(self, client):
        r = client.post("/api/query", content="not json",
                        headers={"Content-Type": "application/json"})
        assert r.status_code == 422

    def test_rag_error_returns_500_with_detail(self, client, mock_rag_system):
        mock_rag_system.query.side_effect = RuntimeError("anthropic down")
        r = client.post("/api/query", json={"query": "x"})
        assert r.status_code == 500
        assert r.json()["detail"] == "anthropic down"

    def test_get_not_allowed(self, client):
        assert client.get("/api/query").status_code == 405


class TestCoursesEndpoint:
    def test_returns_stats(self, client):
        r = client.get("/api/courses")
        assert r.status_code == 200
        assert r.json() == {
            "total_courses": 2,
            "course_titles": ["MCP Course", "Chroma Course"],
        }

    def test_no_courses(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0, "course_titles": []}
        assert client.get("/api/courses").json() == {
            "total_courses": 0, "course_titles": []}

    def test_error_returns_500(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.side_effect = RuntimeError("db gone")
        r = client.get("/api/courses")
        assert r.status_code == 500
        assert r.json()["detail"] == "db gone"

    def test_post_not_allowed(self, client):
        assert client.post("/api/courses").status_code == 405


class TestSessionEndpoint:
    def test_delete_session(self, client, mock_rag_system):
        r = client.delete("/api/session/session_3")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}
        mock_rag_system.session_manager.clear_session.assert_called_once_with("session_3")
