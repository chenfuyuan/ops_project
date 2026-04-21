from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MigrationPaths:
    root_dir: Path
    versions_dir: Path
    env_path: Path
    script_template_path: Path


def migration_paths() -> MigrationPaths:
    root_dir = Path(__file__).resolve().parents[3] / "alembic"
    return MigrationPaths(
        root_dir=root_dir,
        versions_dir=root_dir / "versions",
        env_path=root_dir / "env.py",
        script_template_path=root_dir / "script.py.mako",
    )
