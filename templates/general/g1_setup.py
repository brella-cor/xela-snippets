from pathlib import Path
import sys

start = Path.cwd().resolve()
candidates =  (start, *start.parents)

ROOT = next(
    (p for p in candidates if (p / "pyproject.toml").exists()),
    None,
)
if ROOT is None:
    raise RuntimeError("Run this inside the project; add project.toml")

DATA = ROOT / "data"
RAW = ROOT / "raw"
PROCESSED = DATA / "processed"
FIGURES = ROOT / "reports" / "figures"
MODELS = ROOT / "models"

for folder in (RAW, PROCESSED, FIGURES, MODELS):
    folder.mkdir(parents=True, exist_ok=True)

print(ROOT, sys.executable)

csv_files = sorted(RAW.glob("*.csv"))