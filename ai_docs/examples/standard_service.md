# Standard Service Pattern

Use this pattern when generating `app/business/<domain>/nodes/<unit>/service.py`.

## Purpose
`service.py` owns node-level business use-case orchestration.
It should coordinate business objects, rules, and port calls using business language.

## Responsibilities
- Accept a node-level command or DTO input.
- Validate or normalize through `rules.py` when needed.
- Coordinate business entities and port calls.
- Return a node-level result DTO or domain result object.
- Keep the use-case readable as business flow.

## Must do
- Depend only on business-defined abstractions from `ports.py`.
- Speak in business language, not vendor language.
- Keep orchestration explicit and easy to follow.
- Call adapters only through ports.

## Must not do
- Import vendor SDKs.
- Import HTTP clients, RPC clients, or storage drivers directly.
- Import SQLAlchemy models or ORM sessions directly.
- Perform transport-specific mapping.
- Hide provider-switching logic inside the service.
- Move business decisions into `infrastructure/`.

## Preferred shape
```python
from app.business.<domain>.nodes.<unit>.dto import <Command>, <Result>
from app.business.<domain>.nodes.<unit>.entities import <Entity>
from app.business.<domain>.nodes.<unit>.ports import <PortA>, <PortB>
from app.business.<domain>.nodes.<unit>.rules import <rule_or_validator>


class <Unit>Service:
    def __init__(self, port_a: <PortA>, port_b: <PortB>) -> None:
        self._port_a = port_a
        self._port_b = port_b

    def execute(self, command: <Command>) -> <Result>:
        <rule_or_validator>(command)

        entity = <Entity>.from_command(command)
        context = self._port_a.read_context(entity.<field>)
        artifact = self._port_b.save(entity, context)

        return <Result>(artifact_id=artifact.id)
```

## Reading test for AI
Before finalizing a generated service, check:
- If I replaced each port with a fake, would the service still be testable?
- If the provider changed from local to HTTP, would this file stay unchanged?
- Does this file read like business orchestration instead of integration code?

## Adjacent files
- `node.py` adapts workflow state into service input.
- `ports.py` defines what this service needs.
- `infrastructure/` implements those needs.
- `rules.py` holds reusable business validation and decision logic.
