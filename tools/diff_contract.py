from __future__ import annotations
import difflib
from pathlib import Path
import sys

def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: diff_contract.py OLD_DIR NEW_DIR")
    old = Path(sys.argv[1])
    new = Path(sys.argv[2])
    old_files = {p.relative_to(old).as_posix(): p for p in old.rglob("*") if p.is_file()}
    new_files = {p.relative_to(new).as_posix(): p for p in new.rglob("*") if p.is_file()}
    for key in sorted(set(old_files) | set(new_files)):
        if key not in old_files:
            print(f"ADDED {key}")
            continue
        if key not in new_files:
            print(f"REMOVED {key}")
            continue
        a = old_files[key].read_text(encoding="utf-8").splitlines()
        b = new_files[key].read_text(encoding="utf-8").splitlines()
        if a != b:
            print(f"CHANGED {key}")
            for line in difflib.unified_diff(a, b, fromfile=f"old/{key}", tofile=f"new/{key}", lineterm=""):
                print(line)

if __name__ == "__main__":
    main()
