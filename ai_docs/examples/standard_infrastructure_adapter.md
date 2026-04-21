# Standard Infrastructure Adapter Pattern

Use this pattern when generating `app/business/<domain>/nodes/<unit>/infrastructure/*.py`.

## Purpose
Files under `infrastructure/` implement business-defined ports and translate between business language and external systems, capabilities, or persistence layers.

## Responsibilities
- Implement interfaces declared in `ports.py`.
- Translate business DTOs or entities into provider, capability, repository, or protocol calls.
- Normalize external responses and errors into business-friendly results.
- Keep transport, provider, serialization, auth, retry, and timeout details out of `service.py`.

## Must do
- Depend on the port contract being implemented.
- Keep translation logic close to the boundary.
- Use provider-specific SDKs or storage drivers only here or in lower shared infrastructure layers.
- Return values that match the business-side port contract.

## Must not do
- Add business decision logic that belongs in `service.py` or `rules.py`.
- Leak vendor-specific request or response models into business core files.
- Choose implementations dynamically inside the adapter when that choice belongs in `bootstrap`.
- Turn one adapter into a grab bag for unrelated integrations.

## Preferred shape
```python
from app.business.<domain>.nodes.<unit>.dto import <Query>, <SavedArtifact>
from app.business.<domain>.nodes.<unit>.entities import <Entity>
from app.business.<domain>.nodes.<unit>.ports import ArtifactRepository


class SqlArtifactRepository(ArtifactRepository):
    def __init__(self, session_factory: <SessionFactory>) -> None:
        self._session_factory = session_factory

    def save(self, entity: <Entity>, content: str) -> <SavedArtifact>:
        record = <OrmModel>.from_entity(entity, content)

        with self._session_factory() as session:
            session.add(record)
            session.commit()

        return <SavedArtifact>(artifact_id=record.id)
```

## Another common shape
```python
from app.business.<domain>.nodes.<unit>.dto import <Query>
from app.business.<domain>.nodes.<unit>.ports import ContextReader


class HttpCapabilityContextReader(ContextReader):
    def __init__(self, client: <HttpClient>) -> None:
        self._client = client

    def read_context(self, query: <Query>) -> str:
        response = self._client.post("/context/read", json={"topic": query.topic})
        response.raise_for_status()
        payload = response.json()
        return payload["content"]
```

## Adapter quality test
Before finalizing a generated adapter, check:
- Does this file implement a business-defined port instead of inventing a parallel contract?
- If the provider payload changes, can I update this adapter without touching `service.py`?
- Is all vendor or protocol knowledge confined here?
- Have I accidentally added business branching that should live in rules or services?

## Naming guidance
Prefer names like:
- `SqlArtifactRepository`
- `HttpCapabilityContextReader`
- `S3ArtifactStorage`
- `ExternalValidationClient`

Name the adapter by responsibility first, then provider or transport.
