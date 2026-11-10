"""Graph extraction with Joern (https://joern.io): stage sources, parse, export, convert.

Steps for one project version
  1. stage    copy the in-scope source files (Project.include) from the downloaded archive into
              a work directory outside the repository; for Python 2 sources run lib2to3 there
              and keep, per file, a map from converted line numbers back to original ones
  2. parse    joern-parse <stage> --language pythonsrc|javasrc -o cpg.bin
  3. export   joern --script joern_scripts/export.sc  (CFG + REACHING_DEF edges per method)
  4. convert  codegraphs.extract turns the export into graphs.jsonl / metrics.csv / files.csv

Configuration: JOERN_HOME (folder containing joern-parse[.bat]) and JAVA_HOME (JDK 21), or the
--joern-home / --java-home command line options. See scripts/install_joern.py.
"""
import difflib
import json
import os
import shutil
import subprocess
import warnings
from dataclasses import dataclass, field
from importlib.resources import as_file, files
from pathlib import Path

from codegraphs.download import SourceTree
from codegraphs.projects import Project

FRONTENDS = {"python": "pythonsrc", "java": "javasrc"}


# ----------------------------------------------------------------------------------------------
# configuration
# ----------------------------------------------------------------------------------------------
@dataclass
class JoernConfig:
    joern_home: Path
    java_home: Path

    @classmethod
    def resolve(cls, joern_home=None, java_home=None) -> "JoernConfig":
        jh = Path(joern_home or os.environ.get("JOERN_HOME") or Path("tools") / "joern-cli")
        jv = Path(java_home or os.environ.get("JAVA_HOME") or "")
        if not (jh / _launcher("joern-parse")).exists():
            raise SystemExit(f"Joern not found in {jh}; run `python scripts/install_joern.py` "
                             "or set JOERN_HOME / --joern-home")
        if not jv or not (jv / "bin" / ("java.exe" if os.name == "nt" else "java")).exists():
            raise SystemExit("JDK not found; set JAVA_HOME / --java-home to a JDK 21 installation")
        return cls(jh.resolve(), jv.resolve())

    def env(self) -> dict:
        env = dict(os.environ)
        env["JAVA_HOME"] = str(self.java_home)
        env["PATH"] = str(self.java_home / "bin") + os.pathsep + env.get("PATH", "")
        return env

    def version(self) -> str:
        marker = self.joern_home / "VERSION"  # written by scripts/install_joern.py
        return marker.read_text().strip() if marker.exists() else "unknown"


def _launcher(name: str) -> str:
    return name + ".bat" if os.name == "nt" else name


def _run(cfg: JoernConfig, tool: str, args: list, env_extra: dict = None, cwd: Path = None,
         log: Path = None, timeout: int = 6 * 3600) -> str:
    exe = str(cfg.joern_home / _launcher(tool))
    cmd = (["cmd", "/c", exe] if os.name == "nt" else [exe]) + [str(a) for a in args]
    env = cfg.env()
    env.update(env_extra or {})
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd, timeout=timeout,
                       encoding="utf8", errors="replace")
    text = (r.stdout or "") + "\n" + (r.stderr or "")
    if log is not None:
        log.write_text(text, encoding="utf8")
    if r.returncode != 0:
        raise RuntimeError(f"{tool} failed (exit {r.returncode}); see {log or 'output'}:\n{text[-3000:]}")
    return text


# ----------------------------------------------------------------------------------------------
# staging (+ 2to3 for Python 2 sources)
# ----------------------------------------------------------------------------------------------
@dataclass
class Stage:
    root: Path
    files: list                                   # staged relative paths (POSIX)
    sizes: dict                                   # rel -> bytes of the original file
    line_maps: dict = field(default_factory=dict)  # rel -> list: converted line (1-based) -> original
    converted: bool = False


def _line_map(original: str, converted: str) -> list:
    """List m with m[k] = original line number of converted line k (1-based; m[0] unused).

    Lines inside an equal block map 1:1. Lines of a changed block map to the corresponding
    line of the original block, clamped to its last line; inserted lines map to the original
    line just before the insertion.
    """
    a, b = original.splitlines(), converted.splitlines()
    m = [0] * (len(b) + 2)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        for k in range(j1, j2):
            if tag == "equal":
                orig = i1 + (k - j1)
            elif i2 > i1:
                orig = min(i1 + (k - j1), i2 - 1)
            else:
                orig = max(i1 - 1, 0)
            m[k + 1] = orig + 1
    m[len(b) + 1] = len(a) + 1
    return m


def _py2to3():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from lib2to3 import refactor  # removed in Python 3.13: use Python <= 3.12
    return refactor.RefactoringTool(refactor.get_fixers_from_package("lib2to3.fixes"))


def stage(project: Project, version: str, sources_dir: Path, work_dir: Path) -> Stage:
    root = Path(work_dir) / f"{project.name}-{version}" / "src"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    convert = version in project.py2_versions
    rt = _py2to3() if convert else None
    st = Stage(root=root, files=[], sizes={}, converted=convert)
    with SourceTree(sources_dir, project, version) as tree:
        for rel in (r for r in tree.paths() if project.include(r)):  # already in path_order
            data = tree.read(rel)
            st.sizes[rel] = len(data)
            if rt is not None:
                text = data.decode("utf8", "replace")
                if not text.endswith("\n"):
                    text += "\n"
                try:
                    new = str(rt.refactor_string(text, rel))
                except Exception:  # unconvertible file: keep original (Joern may then reject it)
                    new = text
                if new != text:
                    st.line_maps[rel] = _line_map(text, new)
                data = new.encode("utf8")
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            st.files.append(rel)
    return st


# ----------------------------------------------------------------------------------------------
# parse + export
# ----------------------------------------------------------------------------------------------
def parse_and_export(cfg: JoernConfig, language: str, st: Stage) -> Path:
    work = st.root.parent
    cpg = work / "cpg.bin"
    export = work / "export.jsonl"
    for p in (cpg, export):
        if p.exists():
            p.unlink()
    _run(cfg, "joern-parse", [st.root, "--language", FRONTENDS[language], "-o", cpg],
         cwd=work, log=work / "joern-parse.log")
    script = files("codegraphs").joinpath("joern_scripts/export.sc")
    with as_file(script) as sc:
        out = _run(cfg, "joern", ["--script", sc], cwd=work, log=work / "joern-export.log",
                   env_extra={"CG_CPG": str(cpg), "CG_OUT": str(export)})
    if "CG_EXPORT_DONE" not in out or not export.exists():
        raise RuntimeError(f"Joern export did not finish; see {work / 'joern-export.log'}")
    return export


def read_export(path: Path):
    """Yield the export records (dicts) one by one."""
    with open(path, encoding="utf8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)
