# Standard Ports Pattern

Use this pattern when generating `app/business/<domain>/nodes/<unit>/ports.py`.

## Purpose
`ports.py` defines the business-side dependency boundary.
Ports describe what the business needs from the outside world using business language.

## Responsibilities
- Define repository, reader, writer, validator, or external-collaboration interfaces.
- Express the dependency in business terms.
- Hide transport, provider, SDK, and deployment details from business code.

## Must do
- Name ports by responsibility or capability.
- Keep method names aligned with business intent.
- Use business DTOs, entities, or neutral value types at the boundary.
- Keep each port focused on one clear responsibility.

## Must not do
- Name ports by vendor, SDK, or transport.
- Expose provider-specific request or response types.
- Turn `ports.py` into a grab bag of unrelated interfaces.
- Mirror infrastructure implementation details in the interface shape.

## Preferred shape
```python
from typing import Protocol

from app.business.<domain>.nodes.<unit>.dto import <Query>, <SavedArtifact>
from app.business.<domain>.nodes.<unit>.entities import <Entity>


class ContextReader(Protocol):
    def read_context(self, query: <Query>) -> str: ...


class ArtifactRepository(Protocol):
    def save(self, entity: <Entity>, content: str) -> <SavedArtifact>: ...
```

## Naming guidance
Prefer names like:
- `ContextReader`
- `ArtifactRepository`
- `ContentWriter`
- `ResultPublisher`

Avoid names like:
- `HttpClientPort`
- `OpenAIAdapterPort`
- `SearchApiPort`
- `SDKGateway`

## Port quality test
Before finalizing a generated port, check:
- Would this name still make sense if the implementation moved from local to HTTP?
- Does the interface describe business need instead of implementation mechanism?
- Could multiple adapters implement this without changing the business core?

## Relationship to infrastructure
`infrastructure/` should implement these interfaces and perform:
- protocol translation
- provider mapping
- persistence integration
- error normalization
- timeout and retry behavior where needed

Those concerns belong in adapters, not in the port contract.
