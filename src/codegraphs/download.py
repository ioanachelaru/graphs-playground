"""Download release-tag source archives from GitHub into <sources_dir>/<project>-<version>/."""
import io
import os
import shutil
import tempfile
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


def source_dir(sources_dir: Path, project: Project, version: str) -> Path:
    return Path(sources_dir) / f"{project.name}-{version}"


def download(project: Project, version: str, sources_dir: Path, force: bool = False) -> Path:
    dest = source_dir(sources_dir, project, version)
    if dest.exists() and not force:
        print(f"[skip] {dest} exists")
        return dest
    url = ARCHIVE_URL.format(repo=project.repo, tag=project.tag(version))
    print(f"[get ] {url}")
    fix_ca_env()
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    # Extract to a temp dir next to dest, then move the archive's single top-level folder.
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
        zipfile.ZipFile(io.BytesIO(r.content)).extractall(tmp)
        tops = [p for p in Path(tmp).iterdir() if p.is_dir()]
        if len(tops) != 1:
            raise RuntimeError(f"unexpected archive layout for {project.name} {version}: {tops}")
        shutil.move(str(tops[0]), str(dest))
    print(f"[done] {dest}")
    return dest
