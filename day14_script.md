# Day 14 Script: Packaging The App

## Goal

Today we are packaging the search engine.

Until now, the project was mostly a script:

```text
uv run python main.py
```

That works while developing, but it is not how a real Python app is usually exposed.

For Day 14, we make the app runnable as a package:

```text
uv run python -m search_engine --mode bm25 "operating system scheduling"
```

And we define a console command:

```text
uv run search-engine --mode bm25 "operating system scheduling"
```

The important change is this:

```text
main.py is no longer the only way to run the project.
```

The project now has a package entrypoint.

## Hook

Before packaging, our app is hardcoded.

If we want to change the query, mode, or data path, we edit Python code.

That is fine for early tutorials, but not for a real app.

After packaging, the user can run:

```text
search-engine --mode bm25 --data data "operating system scheduling"
```

Now the app behaves like a command-line tool.

The query is input.

The search mode is input.

The data directory is input.

That is the difference between a script and a packaged app.

## What Packaging Means

Packaging does not mean changing the search algorithm.

Packaging means defining how the project is installed, discovered, and executed.

For this project, packaging has four parts:

1. Project metadata in `pyproject.toml`
2. A CLI module in `search_engine/cli.py`
3. A module entrypoint in `search_engine/__main__.py`
4. A console script named `search-engine`

## pyproject.toml

The `pyproject.toml` file tells Python tooling what this project is.

The key part is:

```toml
[project.scripts]
search-engine = "search_engine.cli:main"
```

This means:

```text
When someone runs search-engine, call main() inside search_engine/cli.py
```

We also add a build backend:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

And because the package folder is named `search_engine`, we explicitly include it:

```toml
[tool.hatch.build.targets.wheel]
packages = ["search_engine"]
```

The distribution name is:

```text
searchengine
```

The import package is:

```text
search_engine
```

Those two names do not have to be identical, but the build config must know which package folder to include.

## CLI Implementation

The CLI lives in:

```text
search_engine/cli.py
```

It accepts:

- `query`
- `--data`
- `--mode`
- `--limit`

Example:

```text
search-engine --mode bm25 --limit 3 "operating system scheduling"
```

The CLI supports these modes:

```python
SEARCH_MODES = ("basic", "ranked", "tfidf", "bm25", "phrase")
```

The important helper is:

```python
def run_search(query: str, file_data: dict[str, str], mode: str = "bm25") -> list[dict]:
    if mode == "basic":
        return basic_search(query, file_data)
    if mode == "ranked":
        ranked_index = build_ranked_inverted_index(file_data)
        return search_ranked_inverted_index_with_snippets(query, ranked_index, file_data)
    if mode == "tfidf":
        tfidf_index = build_tfidf_index(file_data)
        return search_tfidf_index_with_snippets(query, tfidf_index, file_data)
    if mode == "bm25":
        bm25_index = build_bm25_index(file_data)
        return search_bm25_index_with_snippets(query, bm25_index, file_data)
    if mode == "phrase":
        return phrase_search(query, file_data)
```

This keeps the package entrypoint separate from the search logic.

The algorithms stay in:

```text
search_engine/searchengine.py
```

The command-line interface stays in:

```text
search_engine/cli.py
```

That separation is the main design improvement.

## Module Entrypoint

We also add:

```text
search_engine/__main__.py
```

That allows this command:

```text
python -m search_engine --mode bm25 "operating system scheduling"
```

The file is small:

```python
from search_engine.cli import main

raise SystemExit(main())
```

This means the package can be executed directly with Python.

## Demo Output

For the video, run:

```text
uv run python main.py
```

The demo prints:

```text
DAY 14: PACKAGING THE APP
The app can now run as a package CLI.
Command:
uv run search-engine --mode bm25 --limit 3 "operating system scheduling"
--------------------------------------------------
SEARCH ENGINE CLI
MODE: bm25
QUERY: operating system scheduling
```

Then it prints ranked results from the real CLI function.

This proves the demo is not separate fake output.

`main.py` is calling the same CLI entrypoint the package uses.

## Why This Is Useful

Packaging is useful because:

- users can run the app without editing Python files
- scripts can call the search engine with arguments
- tests can call CLI functions directly
- the project has a clear public entrypoint
- the package can later be built, installed, or published

This is also where the project starts looking like a real application instead of a collection of tutorial functions.

## Tradeoffs

Packaging adds structure.

That is useful, but it also adds responsibility.

Now we have to think about:

- package metadata
- version numbers
- console script names
- build backend
- which files are included in the wheel
- how data files are passed into the app

For this tutorial, the `data` directory is still passed as a normal path:

```text
--data data
```

That keeps the packaging simple.

A later production version could include sample data as package data, but that adds more packaging rules.

## Common Mistake

A common mistake is mixing app logic and CLI parsing.

Do not put all search logic inside `argparse`.

The better split is:

```text
searchengine.py -> search algorithms
cli.py -> command-line arguments and output
main.py -> tutorial demo
```

That keeps the code testable.

The tests can call:

```python
run_search("python search", file_data, "bm25")
```

without pretending to be a terminal.

## Closing

Day 14 is not about better ranking.

It is about making the app runnable.

Before:

```text
edit main.py, then run it
```

After:

```text
search-engine --mode bm25 "operating system scheduling"
```

That is the shift from script to package.
