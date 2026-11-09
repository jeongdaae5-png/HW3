"""Advanced, read-only disk usage analyzer with warnings and duplicate detection."""
import argparse
import hashlib
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

CATEGORIES = {"Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic"}, "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".webm", ".m4v"}, "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"}, "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"}, "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rs", ".json", ".xml", ".yml", ".yaml", ".sh"}, "Others": set()}
SIZE_LIMIT = 3 * 1024 ** 3

def human_size(size):
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{int(value)} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024

def category_for(path):
    return next((name for name, exts in CATEGORIES.items() if path.suffix.lower() in exts), "Others")

def get_file_hash(path, chunk_size=1024 * 1024):
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            while chunk := stream.read(chunk_size): digest.update(chunk)
        return digest.hexdigest()
    except OSError: return None

def analyze(root, inactive_days=30):
    totals = defaultdict(lambda: {"size": 0, "count": 0}); candidates = defaultdict(list)
    largest, inactive, errors = [], [], 0; cutoff = time.time() - inactive_days * 86400
    def on_error(_error):
        nonlocal errors
        errors += 1
    for directory, _, filenames in os.walk(root, onerror=on_error, followlinks=False):
        for filename in filenames:
            path = Path(directory) / filename
            try:
                if path.is_symlink(): continue
                stat = path.stat()
            except OSError:
                errors += 1; continue
            size = stat.st_size; category = category_for(path)
            totals[category]["size"] += size; totals[category]["count"] += 1
            largest.append((size, path))
            if size: candidates[size].append(path)
            if stat.st_mtime < cutoff: inactive.append((size, path))
    duplicate_groups, duplicate_waste = [], 0
    for size, paths in candidates.items():
        if len(paths) < 2: continue
        by_hash = defaultdict(list)
        for path in paths:
            digest = get_file_hash(path)
            if digest: by_hash[digest].append(path)
        for same in by_hash.values():
            if len(same) > 1:
                duplicate_groups.append((size, same)); duplicate_waste += size * (len(same) - 1)
    largest.sort(key=lambda item: (-item[0], str(item[1])))
    inactive.sort(key=lambda item: (-item[0], str(item[1])))
    duplicate_groups.sort(key=lambda item: (-item[0], str(item[1][0])))
    return totals, largest[:5], duplicate_groups, duplicate_waste, inactive, errors

def main(argv=None):
    default = Path.home() / "Downloads"
    if not default.is_dir(): default = Path.cwd()
    parser = argparse.ArgumentParser(description="Advanced read-only disk analyzer.")
    parser.add_argument("directory", nargs="?", type=Path, default=default)
    parser.add_argument("--inactive-days", type=int, default=30, metavar="N")
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args(argv)
    if args.inactive_days < 0: parser.error("--inactive-days must be non-negative")
    root = args.directory.expanduser().resolve()
    if not root.is_dir(): parser.error(f"not a directory: {root}")
    totals, largest, duplicates, waste, inactive, errors = analyze(root, args.inactive_days)
    total_size = sum(v["size"] for v in totals.values()); total_count = sum(v["count"] for v in totals.values())
    print(f"\nDisk Analyzer D | {root}\n\nCategory              Files          Size\n" + "-" * 47)
    for name in CATEGORIES:
        item = totals[name]; print(f"{name:<16} {item['count']:>10,} {human_size(item['size']):>16}")
    print("-" * 47 + f"\n{'TOTAL':<16} {total_count:>10,} {human_size(total_size):>16}")
    if total_size > SIZE_LIMIT:
        print(f"WARNING: directory exceeds 3 GiB ({human_size(SIZE_LIMIT)}): {human_size(total_size)}")
    print("\nLargest files:")
    for size, path in largest: print(f"  {human_size(size):>12}  {path}")
    print(f"\nDuplicate groups: {len(duplicates)} (reclaimable: {human_size(waste)})")
    for size, paths in duplicates:
        print(f"  {human_size(size)} each:")
        for path in paths:
            print(f"    {path}")
    print(f"Inactive files (>{args.inactive_days} days): {len(inactive)} ({human_size(sum(s for s, _ in inactive))})")
    if errors: print(f"Skipped entries due to access errors: {errors}")
    return 0

if __name__ == "__main__": sys.exit(main())
