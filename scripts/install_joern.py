"""Install the pinned Joern release into tools/joern-cli (gitignored).

    python scripts/install_joern.py                # Joern v4.0.679 for this OS/CPU
    python scripts/install_joern.py --dest D:/joern

The archive is verified against the release's published SHA-512 before extraction, and the
installed version is written to <dest>/VERSION (recorded in every manifest.json).
Joern also needs a JDK 21 (e.g. `conda install -c conda-forge openjdk=21`); point JAVA_HOME at it.
"""
import argparse
import hashlib
import os
import platform
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import requests

JOERN_VERSION = "v4.0.679"
URL = "https://github.com/joernio/joern/releases/download/{v}/{asset}"


def asset_name() -> str:
    system = {"Windows": "windows", "Linux": "linux", "Darwin": "macos"}[platform.system()]
    arch = "arm64" if platform.machine().lower() in ("arm64", "aarch64") else "x86_64"
    return f"joern-cli-{system}-{arch}.zip"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", type=Path, default=Path("tools") / "joern-cli")
    ap.add_argument("--version", default=JOERN_VERSION)
    a = ap.parse_args()
    for k in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE"):  # see download.fix_ca_env
        v = os.environ.get(k)
        if v and not (Path(v).is_file() and os.access(v, os.R_OK)):
            os.environ.pop(k)
    asset = asset_name()
    url = URL.format(v=a.version, asset=asset)
    expected = requests.get(url + ".sha512", timeout=60).text.split()[0].lower()
    with tempfile.TemporaryDirectory() as tmp:
        zpath = Path(tmp) / asset
        h = hashlib.sha512()
        print(f"[get ] {url}")
        with requests.get(url, stream=True, timeout=120) as r, open(zpath, "wb") as fh:
            r.raise_for_status()
            for chunk in r.iter_content(8 << 20):
                fh.write(chunk)
                h.update(chunk)
        if h.hexdigest() != expected:
            print("SHA-512 mismatch; aborting", file=sys.stderr)
            return 1
        print("[ok  ] SHA-512 verified")
        extract_to = Path(tmp) / "x"
        zipfile.ZipFile(zpath).extractall(extract_to)
        src = extract_to / "joern-cli"
        if a.dest.exists():
            shutil.rmtree(a.dest)
        a.dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(a.dest))
    if os.name != "nt":  # zipfile drops executable bits: restore them on launcher scripts
        for p in a.dest.rglob("*"):
            if p.is_file() and p.suffix in ("", ".sh") and not p.name.startswith("."):
                p.chmod(p.stat().st_mode | 0o111)
    (a.dest / "VERSION").write_text(a.version + "\n")
    print(f"[done] Joern {a.version} in {a.dest.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
