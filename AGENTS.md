# AGENTS.md

## Purpose

Small Python search-engine project used for day-by-day search concepts: tokenization, inverted indexes, ranked search, snippets, stopwords, TF-IDF, BM25, ranking explainability, phrase search, Boolean search, and packaging.

## Where To Work

- Core search helpers live in `search_engine/searchengine.py`.
- CLI/package entrypoint code lives in `search_engine/cli.py`.
- Module execution entrypoint lives in `search_engine/__main__.py`.
- Demo/runtime code lives in `main.py`.
- Tests live in `tests/engine_test.py`.
- Documents used by the demo live in `data/`.
- Tutorial narration for Day 13 Boolean search lives in `day13_script.md`.
- Tutorial narration for Day 14 packaging lives in `day14_script.md`.

## Normal Commands

- Run the demo: `uv run python main.py`
- Run the package module: `uv run python -m search_engine --mode bm25 "operating system scheduling"`
- Run the console script after sync/install: `uv run search-engine --mode bm25 "operating system scheduling"`
- Run tests: `uv run python -m pytest`

## Change Rules

- Keep `tokenize()` as the plain tokenizer unless intentionally changing all search behavior.
- Use `tokenize_with_stopwords()` for normal ranked search.
- Boolean search is a filter over document sets; keep `AND`, `OR`, and `NOT` behavior explicit and easy to explain.
- Keep CLI argument parsing in `search_engine/cli.py`; keep search algorithms in `search_engine/searchengine.py`.
- `index_data.json` is a generated ranked index cache; rebuild or delete it if index preprocessing changes and the cached behavior matters.

## Engineering Bar

- Preserve simple data structures that are easy to explain in a tutorial.
- Keep search result shapes consistent: use dictionaries with `file_name`, plus `score`, `snippet`, or concept-specific explanation fields when available.
- Add tests when changing tokenization, indexing, ranking, phrase matching, Boolean logic, explanations, or result shapes.

## Verification Bar

- Before finishing code changes, run `uv run python -m pytest`.
- Run `uv run python main.py` when changing demo output.

## Avoid

- Do not introduce external dependencies for basic search concepts unless the day explicitly calls for them.
- Do not commit virtual environments, caches, or generated Python bytecode.
