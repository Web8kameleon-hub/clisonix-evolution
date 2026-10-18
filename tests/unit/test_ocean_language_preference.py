import ast
import asyncio
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "ocean-core/ocean_core_full.py"


async def select_language(requested, detected, detected_confidence=0.99, strict=False):
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    fn = next(
        n for n in tree.body
        if isinstance(n, ast.AsyncFunctionDef)
        and n.name == "process_query_full"
    )
    block = next(
        n for n in fn.body
        if isinstance(n, ast.If)
        and isinstance(n.test, ast.Name)
        and n.test.id == "strict_language_lock"
    )

    async def resolve_language_name(code):
        return {"sq": "Albanian", "de": "German", "en": "English"}[code]

    class Logger:
        def info(self, *args):
            pass

    namespace = {
        "requested_language": requested,
        "detected_lang_code": detected,
        "detected_lang_name": "Detected",
        "detected_confidence": detected_confidence,
        "strict_language_lock": bool(requested and strict),
        "resolve_language_name": resolve_language_name,
        "engines_used": [],
        "logger": Logger(),
    }

    module = ast.fix_missing_locations(ast.Module(body=[block], type_ignores=[]))
    compiled = compile(module, "<language-selection>", "exec",
                       flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    await eval(compiled, namespace)

    return namespace["lang_code"], namespace["confidence"]


def test_albanian_preference():
    assert asyncio.run(select_language("sq", "it"))[0] == "sq"


def test_german_preference():
    assert asyncio.run(select_language("de", "en"))[0] == "de"


def test_english_preference():
    assert asyncio.run(select_language("en", "sq"))[0] == "en"


def test_auto_detection():
    assert asyncio.run(select_language("", "sq"))[0] == "sq"


def test_strict_albanian():
    assert asyncio.run(select_language("sq", "en", strict=True))[0] == "sq"


def test_preference_does_not_fabricate_detector_confidence():
    assert asyncio.run(select_language("sq", "it", 0.42))[1] == 0.42
