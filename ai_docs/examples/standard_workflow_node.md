# Standard Workflow Node Pattern

Use this pattern when generating `app/business/<domain>/nodes/<unit>/node.py`.

## Purpose
`node.py` is the workflow-facing adapter for a business step.
It converts workflow state into a service command, invokes the service, and maps the result back into workflow state.

## Responsibilities
- Accept workflow state or upstream node output.
- Extract only the data required for this step.
- Build a node-level command or DTO.
- Call `service.py`.
- Write back only the minimal result needed by downstream workflow steps.

## Must do
- Treat workflow state as a boundary input, not as an unlimited mutable bag.
- Keep node logic thin and focused on adaptation.
- Use explicit DTOs or command objects when passing data into the service.
- Return a bounded state update or result mapping.

## Must not do
- Put business rules here.
- Call SDKs, repositories, or external services directly.
- Recreate orchestration that belongs in `service.py`.
- Expand workflow state with unrelated intermediate details.

## Preferred shape
```python
from app.business.<domain>.nodes.<unit>.dto import <Command>
from app.business.<domain>.nodes.<unit>.service import <Unit>Service
from app.business.<domain>.workflow.state import WorkflowState


class <Unit>Node:
    def __init__(self, service: <Unit>Service) -> None:
        self._service = service

    def run(self, state: WorkflowState) -> WorkflowState:
        command = <Command>(
            request_id=state.request_id,
            topic=state.topic,
        )

        result = self._service.execute(command)

        return state.model_copy(update={
            "artifact_id": result.artifact_id,
        })
```

## State discipline
When generating a node, prefer this mindset:
- read only the fields this node needs
- write back only fields that truly need to cross node boundaries
- keep temporary calculations inside the node or service, not in global workflow state

`workflow/state.py` is a high-sensitivity boundary and must stay minimal.

## Node quality test
Before finalizing a generated node, check:
- If workflow state changed shape slightly, would only this adapter need adjustment?
- Does this file contain only input mapping, service invocation, and output mapping?
- Did I accidentally put business validation or integration logic here?
- Am I writing too much transient data back into workflow state?

## Relationship to adjacent files
- `workflow/state.py` defines the shared cross-node state.
- `node.py` adapts that state for one step.
- `service.py` performs business orchestration.
- `ports.py` and `infrastructure/` handle dependency boundaries.
