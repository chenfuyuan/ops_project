from dataclasses import dataclass
from typing import Generic, TypeVar

SuccessT = TypeVar("SuccessT")
ErrorT = TypeVar("ErrorT")


@dataclass(slots=True, frozen=True)
class Result(Generic[SuccessT, ErrorT]):
    value: SuccessT | None = None
    error: ErrorT | None = None

    @property
    def is_ok(self) -> bool:
        return self.error is None
