from dataclasses import dataclass, field


@dataclass(slots=True)
class ModuleRegistry:
    modules: list[str] = field(default_factory=list)


def create_module_registry() -> ModuleRegistry:
    return ModuleRegistry()
