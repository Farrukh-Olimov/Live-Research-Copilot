from pathlib import Path

APP_ROOT = Path.cwd()
LOG_DIR = APP_ROOT.joinpath("logs")
LOG_DIR.mkdir(exist_ok=True)
