from dataclasses import dataclass
from uuid import uuid4

from fastapi import FastAPI, Request


@dataclass(slots=True, frozen=True)
class RequestContext:
    request_id: str


def register_request_context_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def attach_request_context(request: Request, call_next):
        request.state.request_context = RequestContext(
            request_id=request.headers.get("x-request-id", str(uuid4()))
        )
        return await call_next(request)
