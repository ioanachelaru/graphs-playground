"""Download release sources (GitHub tag archives) into sources/<project>-<version>/.

Usage:
    python src/download_sources.py --project django   --versions 1.0 1.1
    python src/download_sources.py --project django   --all
    python src/download_sources.py --project activemq --versions 5.0.0
"""
import argparse
import io
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"

PROJECTS = {
    "django": {
        "repo": "django/django",
        "tag": "{v}",  # Django tags have no trailing ".0" patch part: 1.0, 1.1, ... 4.2
        "versions": [
            "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "1.10", "1.11",
            "2.0", "2.1", "2.2", "3.0", "3.1", "3.2", "4.0", "4.1", "4.2",
        ],
    },
    "activemq": {
        "repo": "apache/activemq",
        "tag": "activemq-{v}",  # e.g. activemq-5.0.0
        "versions": ["5.0.0"],
    },
}
URL = "https://codeload.github.com/{repo}/zip/refs/tags/{tag}"


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


def download(project: str, version: str, force: bool = False) -> Path:
    cfg = PROJECTS[project]
    dest = SOURCES / f"{project}-{version}"
    if dest.exists() and not force:
        print(f"[skip] {dest} exists")
        return dest
    url = URL.format(repo=cfg["repo"], tag=cfg["tag"].format(v=version))
    print(f"[get ] {url}")
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    SOURCES.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    # Extract to a temp dir, then move the archive's single top-level folder to `dest`.
    with tempfile.TemporaryDirectory(dir=SOURCES) as tmp:
        zipfile.ZipFile(io.BytesIO(r.content)).extractall(tmp)
        tops = [p for p in Path(tmp).iterdir() if p.is_dir()]
        assert len(tops) == 1, f"unexpected archive layout for {project} {version}: {tops}"
        shutil.move(str(tops[0]), str(dest))
    print(f"[done] {dest}")
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, choices=sorted(PROJECTS))
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--versions", nargs="+")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-download even if present")
    a = ap.parse_args()
    _fix_ca_env()
    for v in (PROJECTS[a.project]["versions"] if a.all else a.versions):
        download(a.project, v, a.force)


if __name__ == "__main__":
    main()
