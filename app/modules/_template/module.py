from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ModuleDefinition:
    name: str


MODULE = ModuleDefinition(name="replace_me")
