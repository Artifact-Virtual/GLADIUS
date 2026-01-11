import os
import sys
import shutil
from pathlib import Path

# ensure project root is importable
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from scripts.organizer import sync


def test_organizer_copies_and_is_idempotent(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    (src / "reports").mkdir(parents=True)
    (src / "charts").mkdir(parents=True)

    f1 = src / "reports" / "r1.md"
    f1.write_text("report1")
    f2 = src / "charts" / "c1.png"
    f2.write_bytes(b"pngdata")

    copied = sync(src, dest, dry_run=False)
    assert copied == 2
    assert (dest / "reports" / "r1.md").exists()
    assert (dest / "charts" / "c1.png").exists()
    assert (dest / "file_index.json").exists()

    # Run again, idempotent (no copies if files are unchanged)
    copied2 = sync(src, dest, dry_run=False)
    assert copied2 == 0

    # Modify a source file and ensure it updates destination
    f1.write_text("updated")
    copied3 = sync(src, dest, dry_run=False)
    assert copied3 == 1
    assert (dest / "reports" / "r1.md").read_text() == "updated"
