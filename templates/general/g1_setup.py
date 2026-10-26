from pathlib import Path
import sys
import warnings

start = Path.cwd().resolve()
ancestors = (start, *start.parents)

# Your structure: project / notebooks / datapull
notebooks_folder = next(
    (
        folder
        for folder in ancestors
        if folder.name.lower() == "notebooks"
    ),
    None,
)

if notebooks_folder is not None:
    ROOT = notebooks_folder.parent

elif (start / "notebooks").is_dir():
    ROOT = start

else:
    ROOT = next(
        (
            folder
            for folder in ancestors
            if folder != Path(folder.anchor)
            and (
                (folder / ".git").exists()
                or (folder / "pyproject.toml").is_file()
            )
        ),
        None,
    )

    if ROOT is None:
        ROOT = start

        warnings.warn(
            f"Could not identify the project root above {start}. "
            f"Using the current directory: {ROOT}",
            stacklevel=2,
        )

if not (ROOT / ".git").exists():
    warnings.warn(
        f"No .git file or directory found in {ROOT}. "
        "Continuing without Git.",
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
    "Working directory": start,
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