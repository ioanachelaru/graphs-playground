"""Download release-tag source archives from GitHub and read source files from them.

Each version is kept as the downloaded zip, sources/<project>-<version>.zip, and read directly
(no extraction). Paths are POSIX paths relative to the version root, with the archive's
top-level "<repo>-<tag>/" folder stripped, e.g. "django/db/models/base.py".
"""
import io
import os
import time
import zipfile
from pathlib import Path

import requests

from codegraphs.projects import Project

ARCHIVE_URL = "https://codeload.github.com/{repo}/zip/refs/tags/{tag}"


def path_order(rel: str) -> list:
    """Sort key for source paths: case-insensitive per path component, identical on every OS."""
    return [part.lower() for part in rel.split("/")]


def fix_ca_env() -> None:
    """Drop CA-bundle env vars that point to missing/unreadable files (they break `requests`).

    Some corporate TLS setups export REQUESTS_CA_BUNDLE etc. pointing to a file the current
    process cannot read; requests then fails before connecting.
    """
    for k in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE"):
        v = os.environ.get(k)
        if not v:
            continue
        try:
            ok = Path(v).is_file() and os.access(v, os.R_OK)
        except OSError:
            ok = False
        if not ok:
            os.environ.pop(k)


def archive_path(sources_dir: Path, project: Project, version: str) -> Path:
    return Path(sources_dir) / f"{project.name}-{version}.zip"


def download(project: Project, version: str, sources_dir: Path, force: bool = False) -> Path:
    dest = archive_path(sources_dir, project, version)
    if dest.exists() and not force:
        print(f"[skip] {dest} exists")
        return dest
    url = ARCHIVE_URL.format(repo=project.repo, tag=project.tag(version))
    print(f"[get ] {url}")
    fix_ca_env()
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    zipfile.ZipFile(io.BytesIO(r.content)).testzip()  # fail early on a corrupt archive
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(dest.name + ".partial")
    partial.write_bytes(r.content)
    for attempt in range(20):  # antivirus / sandbox may hold the new file for a moment (Windows)
        try:
            os.replace(partial, dest)
            break
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.25)
    print(f"[done] {dest} ({len(r.content) / 1e6:.1f} MB)")
    return dest


class SourceTree:
    """Read-only view of one version's downloaded zip."""

    def __init__(self, sources_dir: Path, project: Project, version: str):
        self.path = archive_path(sources_dir, project, version)
        if not self.path.exists():
            raise FileNotFoundError(f"no sources at {self.path}")
        self._zip = zipfile.ZipFile(self.path)
        tops = {n.split("/", 1)[0] for n in self._zip.namelist() if n.strip("/")}
        if len(tops) != 1:
            raise RuntimeError(f"unexpected archive layout in {self.path}: {sorted(tops)[:5]}")
        self._members = {}
        for info in self._zip.infolist():
            rel = info.filename.split("/", 1)[1] if "/" in info.filename else ""
            if rel and not info.is_dir():
                self._members[rel] = info

    def paths(self) -> list:
        """All file paths in the archive, in path_order."""
        return sorted(self._members, key=path_order)

    def read(self, rel: str) -> bytes:
        return self._zip.read(self._members[rel])

    def close(self) -> None:
        self._zip.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
