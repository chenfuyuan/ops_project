from pathlib import Path

from scripts.dev_start import build_run_options


def test_build_run_options_point_uvicorn_at_the_project_root() -> None:
    run_options = build_run_options()

    assert run_options["app_dir"] == str(Path(__file__).resolve().parents[2])
