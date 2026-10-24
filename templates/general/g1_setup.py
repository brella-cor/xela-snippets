from pathlib import Path
import sys
import warnings

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
    ROOT = start
    warnings.warn(
        f"No Git repository or pyproject.toml found above {start}. "
        f"Using the current directory as the project root: {ROOT}",
        stacklevel=2,
    )
elif not (ROOT / ".git").exists():
    warnings.warn(
        f"No .git file or directory found in {ROOT}. "
        "Continuing with the project root identified by pyproject.toml.",
        stacklevel=2,
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
    print(f"{name:<18}: {path}")

print(f"{'Python executable':<18}: {sys.executable}")

csv_files = sorted(RAW.glob("*.csv"))