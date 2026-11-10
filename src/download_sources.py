"""Download Django release sources (GitHub tag archives) into sources/django-<version>/.

Usage:
    python src/download_sources.py --versions 1.0 1.1
    python src/download_sources.py --all          # every version in DJANGO_VERSIONS
"""
import argparse
import io
import os
import shutil
import zipfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
URL = "https://codeload.github.com/django/django/zip/refs/tags/{tag}"

# Django release tags 1.0 .. 4.2 (tag names have no trailing ".0" patch part).
DJANGO_VERSIONS = [
    "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "1.10", "1.11",
    "2.0", "2.1", "2.2", "3.0", "3.1", "3.2", "4.0", "4.1", "4.2",
]


def _fix_ca_env():
    """Drop CA-bundle env vars that point to files which do not exist (breaks requests)."""
    for k in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE"):
        v = os.environ.get(k)
        if not v:
            continue
        try:
            ok = Path(v).is_file() and os.access(v, os.R_OK)
        except OSError:  # e.g. PermissionError on a locked corporate bundle
            ok = False
        if not ok:
            os.environ.pop(k)


def download(version: str, force: bool = False) -> Path:
    dest = SOURCES / f"django-{version}"
    if dest.exists() and not force:
        print(f"[skip] {dest} exists")
        return dest
    print(f"[get ] {URL.format(tag=version)}")
    r = requests.get(URL.format(tag=version), timeout=300)
    r.raise_for_status()
    SOURCES.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    # The archive's top-level folder is "django-<tag>", i.e. exactly `dest`.
    zipfile.ZipFile(io.BytesIO(r.content)).extractall(SOURCES)
    assert dest.exists(), f"unexpected archive layout for {version}"
    n_py = sum(1 for _ in (dest / "django").rglob("*.py"))
    print(f"[done] {dest} ({n_py} .py files under django/)")
    return dest


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--versions", nargs="+")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-download even if present")
    a = ap.parse_args()
    _fix_ca_env()
    for v in (DJANGO_VERSIONS if a.all else a.versions):
        download(v, a.force)


if __name__ == "__main__":
    main()
