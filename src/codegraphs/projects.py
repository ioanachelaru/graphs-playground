"""Registry of the projects this pipeline knows how to download and analyse."""
from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Project:
    name: str
    repo: str                       # GitHub "owner/name"
    tag_format: str                 # release tag for a version, e.g. "activemq-{v}"
    language: str                   # key in codegraphs.languages.LANGUAGES
    include: Callable[[str], bool]  # selects source files by path relative to the version root
    scope: str                      # human-readable description of `include` (for manifests)
    versions: tuple = field(default_factory=tuple)

    def tag(self, version: str) -> str:
        return self.tag_format.format(v=version)


def _django_include(rel: str) -> bool:
    return rel.startswith("django/") and rel.endswith(".py")


def _java_main_include(rel: str) -> bool:
    return rel.endswith(".java") and "/src/main/java/" in "/" + rel


PROJECTS = {
    p.name: p
    for p in (
        Project(
            name="django",
            repo="django/django",
            tag_format="{v}",
            language="python",
            include=_django_include,
            scope="django/ package only",
            versions=("1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9",
                      "2.0", "2.1", "2.2",
                      "3.0", "3.1", "3.2",
                      "4.0", "4.1", "4.2",
                      "5.0", "5.1", "5.2"),
        ),
        Project(
            name="activemq",
            repo="apache/activemq",
            tag_format="activemq-{v}",
            language="java",
            include=_java_main_include,
            scope="**/src/main/java (production code of all modules)",
            versions=("5.0.0", "5.1.0", "5.2.0", "5.3.0", "5.8.0"),
        ),
    )
}


def get_project(name: str) -> Project:
    try:
        return PROJECTS[name]
    except KeyError:
        raise SystemExit(f"unknown project {name!r}; known: {', '.join(sorted(PROJECTS))}")
