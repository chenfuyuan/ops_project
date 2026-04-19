from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.interfaces.http.middleware.request_context import register_request_context_middleware


def test_request_context_middleware_attaches_placeholder_state() -> None:
    app = FastAPI()
    register_request_context_middleware(app)

    @app.get("/probe")
    async def probe(request: Request) -> dict[str, str]:
        request_context = request.state.request_context
        return {"request_id": request_context.request_id}

    response = TestClient(app).get("/probe")

    assert response.status_code == 200
    assert response.json()["request_id"]
