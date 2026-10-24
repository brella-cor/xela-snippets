import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "snippets.json"
OUTPUT = ROOT / "dist" / "xela.code-snippets"


def escape_snippet(text: str) -> str:
    """Preserve characters that VS Code treats as snippet syntax."""
    return (
        text.replace("\\", "\\\\")
        .replace("$", "\\$")
        .replace("}", "\\}")
    )


def build_snippets() -> None:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))

    if not isinstance(entries, list):
        raise ValueError("snippets.json must contain a list of entries.")

    snippets = {}
    prefixes = set()

    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Each manifest entry must be an object.")

        for field in ("name", "prefix", "description", "source"):
            value = entry.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Each entry needs a nonempty '{field}' string."
                )

        name = entry["name"]
        prefix = entry["prefix"]
        source = ROOT / entry["source"]

        if name in snippets:
            raise ValueError(f"Duplicate snippet name: {name}")

        if prefix in prefixes:
            raise ValueError(f"Duplicate snippet prefix: {prefix}")

        if not source.is_file():
            raise FileNotFoundError(f"Template not found: {source}")

        text = source.read_text(encoding="utf-8-sig")

        # Validate syntax without executing imports or other code.
        compile(text, str(source), "exec")

        snippets[name] = {
            "scope": "python",
            "prefix": prefix,
            "description": entry["description"],
            "body": [
                *[
                    escape_snippet(line)
                    for line in text.splitlines()
                ],
                "",
                "$0",
            ],
        }

        prefixes.add(prefix)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(snippets, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Built {len(snippets)} snippets.")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    try:
        build_snippets()
    except (OSError, ValueError, SyntaxError) as error:
        raise SystemExit(f"Build failed: {error}")