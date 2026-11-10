"""Language front-ends. Add a language by implementing `Language` and registering it here."""
from codegraphs.languages.base import Language
from codegraphs.languages.java import JavaLanguage
from codegraphs.languages.python import PythonLanguage

LANGUAGES = {lang.name: lang for lang in (PythonLanguage(), JavaLanguage())}


def get_language(name: str) -> Language:
    return LANGUAGES[name]


__all__ = ["Language", "LANGUAGES", "get_language"]
