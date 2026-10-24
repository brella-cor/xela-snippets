from pathlib import Path
import sys

start = Path.cwd().resolve()

ROOT = next(
    (
        folder
        for folder in (start, *start.parents)
        if (folder / ".git").exists()
        or (folder / "pyproject.toml").is_file()
    ),
    None,
)

if ROOT is None:
    raise RuntimeError(
        f"No project root found above {start}. "
        "Open the notebook inside your Git repository."
    )

DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
FIGURES = ROOT / "reports" / "figures"
MODELS = ROOT / "models"

for folder in (RAW, PROCESSED, FIGURES, MODELS):
    folder.mkdir(parents=True, exist_ok=True)

directories = {
    "Project root": ROOT,
    "Data": DATA,
    "Raw data": RAW,
    "Processed data": PROCESSED,
    "Figures": FIGURES,
    "Models": MODELS,
}

for name, path in directories.items():
    print(f"{name:<16}: {path}")

print(f"{'Python executable':<16}: {sys.executable}")

csv_files = sorted(RAW.glob("*.csv"))
