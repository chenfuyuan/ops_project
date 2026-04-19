import os
from pathlib import Path

import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_run_options() -> dict[str, str | int | bool]:
    return {
        "host": os.getenv("APP_HOST", "127.0.0.1"),
        "port": int(os.getenv("APP_PORT", "8000")),
        "reload": False,
        "app_dir": str(PROJECT_ROOT),
    }


def main() -> None:
    uvicorn.run("app.main:app", **build_run_options())


if __name__ == "__main__":
    main()
