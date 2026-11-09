import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".webm", ".m4v"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rs", ".json", ".xml", ".yml", ".yaml", ".sh"},
    "Others": set(),
}

COLORS = {
    "Images": "\033[35m",
    "Videos": "\033[31m",
    "Documents": "\033[34m",
    "Archives": "\033[33m",
    "Code": "\033[36m",
    "Others": "\033[37m",
}
RESET = "\033[0m"


def human_size(size):
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024


def category_for(path):
    extension = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return "Others"


def progress_bar(percent, width=18):
    filled = round(width * percent / 100)
    return f"[{'=' * filled}{'-' * (width - filled)}] {percent:5.1f}%"


def analyze(root):
    totals = defaultdict(lambda: {"size": 0, "count": 0})
    errors = 0

    def on_walk_error(_error):
        nonlocal errors
        errors += 1

    for directory, _, filenames in os.walk(root, onerror=on_walk_error, followlinks=False):
        for filename in filenames:
            path = Path(directory) / filename
            try:
                if path.is_symlink():
                    continue
                size = path.stat().st_size
            except OSError:
                errors += 1
                continue

            category = category_for(path)
            totals[category]["size"] += size
            totals[category]["count"] += 1

    return totals, errors


def main():
    default_path = Path.home() / "Downloads"
    if not default_path.is_dir():
        default_path = Path.cwd()

    parser = argparse.ArgumentParser(description="Analyze file usage by category.")
    parser.add_argument("directory", nargs="?", type=Path, default=default_path,
                        help=f"directory to scan (default: {default_path})")
    parser.add_argument("--no-color", action="store_true", help="disable colored output")
    args = parser.parse_args()

    root = args.directory.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    use_color = (
        not args.no_color
        and sys.stdout.isatty()
        and "NO_COLOR" not in os.environ
    )

    print(f"\n  Disk Analyzer  |  {root}\n")
    totals, errors = analyze(root)
    overall_size = sum(item["size"] for item in totals.values())
    overall_count = sum(item["count"] for item in totals.values())

    name_width = max(len(name) for name in CATEGORIES)
    print(f"  {'Category':<{name_width}}  {'Files':>8}  {'Size':>12}  {'Usage':<28}")
    print(f"  {'-' * name_width}  {'-' * 8}  {'-' * 12}  {'-' * 28}")

    for category in CATEGORIES:
        item = totals[category]
        percent = item["size"] / overall_size * 100 if overall_size else 0
        bar = progress_bar(percent)
        label = f"{category:<{name_width}}"
        if use_color:
            label = f"{COLORS[category]}{label}{RESET}"
            bar = f"{COLORS[category]}{bar}{RESET}"
        print(f"  {label}  {item['count']:>8,}  {human_size(item['size']):>12}  {bar}")

    print(f"  {'-' * name_width}  {'-' * 8}  {'-' * 12}  {'-' * 28}")
    print(f"  {'TOTAL':<{name_width}}  {overall_count:>8,}  {human_size(overall_size):>12}")
    if errors:
        print(f"\n  Skipped {errors} file(s) that could not be read.")
    print()


if __name__ == "__main__":
    main()
