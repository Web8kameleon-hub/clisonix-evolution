"""Restore the existing model volume and let fallback requests reach the model."""
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
source = root / 'ocean-core/ocean_core_full.py'
text = source.read_text(encoding='utf-8')
text = text.replace('if _is_low_value_fast_answer(fast_text):', 'if str(getattr(fast_real, "source", "")) == "conversational_fallback" or _is_low_value_fast_answer(fast_text):')
source.write_text(text, encoding='utf-8', newline='\n')
compose = root / 'docker-compose.unified.yml'
text = compose.read_text(encoding='utf-8')
text = text.replace("      MODEL: qwen2.5:7b", "      MODEL: llama3.1:8b")
text = text.replace('  ollama_data:\n    driver: local', '  ollama_data:\n    external: true\n    name: clisonix_ollama_data')
compose.write_text(text, encoding='utf-8', newline='\n')
auth = root / 'apps/web/app/api/clisonix-auth/_lib.ts'
if auth.exists():
    text = auth.read_text(encoding='utf-8').replace('"../../_lib/upstream"', '"../_lib/upstream"')
    auth.write_text(text, encoding='utf-8', newline='\n')
