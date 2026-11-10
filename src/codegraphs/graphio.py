"""Reading and writing the output files (graphs.jsonl.gz, CSV, JSON)."""
import csv
import gzip
import io
import json
from pathlib import Path


def write_jsonl_gz(path: Path, records) -> None:
    """One compact JSON object per line, gzip level 9 with mtime=0 and no stored file name, so
    identical records always give identical bytes."""
    with open(path, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0,
                                                compresslevel=9) as gz:
        with io.TextIOWrapper(gz, encoding="utf8", newline="\n") as fh:
            for r in records:
                fh.write(json.dumps(r, separators=(",", ":")) + "\n")


def read_jsonl_gz(path: Path):
    """Yield the records of a graphs.jsonl.gz file."""
    with gzip.open(path, "rt", encoding="utf8") as fh:
        for line in fh:
            yield json.loads(line)


def write_csv(path: Path, rows: list) -> None:
    """CSV with the keys of the first row as header (empty file when there are no rows)."""
    with open(path, "w", newline="", encoding="utf8") as fh:
        if rows:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)


def write_json(path: Path, obj) -> None:
    with open(path, "w", encoding="utf8", newline="\n") as fh:
        fh.write(json.dumps(obj, indent=2) + "\n")
