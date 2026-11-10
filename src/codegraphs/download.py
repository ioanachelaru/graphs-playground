"""Download release-tag source archives from GitHub and read source files from them.

Sources are kept as the downloaded zip, sources/<project>-<version>.zip, and read directly
from it (no extraction: faster, less disk, and avoids file-system races when creating thousands
of folders). A previously extracted folder sources/<project>-<version>/ is still supported.
"""
import io
import os
import time
import zipfile
from pathlib import Path

import requests

from codegraphs.projects import Project

ARCHIVE_URL = "https://codeload.github.com/{repo}/zip/refs/tags/{tag}"


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


def legacy_dir(sources_dir: Path, project: Project, version: str) -> Path:
    return Path(sources_dir) / f"{project.name}-{version}"


def _retry(fn, attempts: int = 20, delay: float = 0.25):
    """Retry transient Windows file errors (e.g. antivirus/sandbox briefly holding a file)."""
    for i in range(attempts):
        try:
            return fn()
        except PermissionError:
            if i == attempts - 1:
                raise
            time.sleep(delay)


def download(project: Project, version: str, sources_dir: Path, force: bool = False) -> Path:
    dest = archive_path(sources_dir, project, version)
    if not force and (dest.exists() or legacy_dir(sources_dir, project, version).is_dir()):
        print(f"[skip] {project.name} {version} already downloaded")
        return dest
    url = ARCHIVE_URL.format(repo=project.repo, tag=project.tag(version))
    print(f"[get ] {url}")
    fix_ca_env()
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    zipfile.ZipFile(io.BytesIO(r.content)).testzip()  # fail early on a bad archive
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(dest.name + ".partial")
    partial.write_bytes(r.content)
    _retry(lambda: os.replace(partial, dest))
    print(f"[done] {dest} ({len(r.content) / 1e6:.1f} MB)")
    return dest


class SourceTree:
    """Read-only view of one version's sources: a GitHub tag zip or an extracted folder.

    Paths are POSIX paths relative to the version root (the archive's top folder stripped),
    e.g. "django/db/models/base.py".
    """

    def __init__(self, sources_dir: Path, project: Project, version: str):
        self.zip_path = archive_path(sources_dir, project, version)
        self.dir_path = legacy_dir(sources_dir, project, version)
        self._zip = None
        self._members = {}
        if self.zip_path.exists():
            self._zip = zipfile.ZipFile(self.zip_path)
            tops = {n.split("/", 1)[0] for n in self._zip.namelist() if n.strip("/")}
            if len(tops) != 1:
                raise RuntimeError(f"unexpected archive layout in {self.zip_path}: {sorted(tops)[:5]}")
            for info in self._zip.infolist():
                rel = info.filename.split("/", 1)[1] if "/" in info.filename else ""
                if rel and not info.is_dir():
                    self._members[rel] = info
        elif not self.dir_path.is_dir():
            raise FileNotFoundError(f"no sources at {self.zip_path} or {self.dir_path}")

    @property
    def location(self) -> Path:
        return self.zip_path if self._zip is not None else self.dir_path

    def paths(self) -> list:
        if self._zip is not None:
            return list(self._members)
        return [p.relative_to(self.dir_path).as_posix()
                for p in self.dir_path.rglob("*") if p.is_file()]

    def read(self, rel: str) -> bytes:
        if self._zip is not None:
            return self._zip.read(self._members[rel])
        return (self.dir_path / rel).read_bytes()

    def close(self) -> None:
        if self._zip is not None:
            self._zip.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
