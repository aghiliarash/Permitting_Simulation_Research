"""Verify the distributed release-file checksums."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]
for line in (ROOT/'SHA256SUMS').read_text().splitlines():
    digest, relative=line.split('  ',1)
    path=ROOT/relative
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
        raise SystemExit('Checksum mismatch: '+relative)
print('All release checksums verified.')
