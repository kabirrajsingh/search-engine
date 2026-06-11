# Day 13 Script: Boolean Search

## Goal

Today we are adding Boolean search.

So far, most of our search modes have asked:

```text
Which documents match these query words?
```

Boolean search asks something stricter:

```text
Which documents satisfy this exact logic?
```

The three operators are:

- `AND`
- `OR`
- `NOT`

## Hook

Search for:

```text
python AND search NOT database
```

What does the user mean?

They want documents that contain:

```text
python
search
```

but do not contain:

```text
database
```

Normal loose search does not understand that logic.

In our demo, normal search returns this:

```text
BEFORE: normal search treats query words as loose matches
FILE_NAME: python_search.txt
FILE_NAME: python_database.txt
FILE_NAME: search_only.txt
FILE_NAME: python_only.txt
FILE_NAME: database_only.txt
```

That is too broad.

It includes:

- a document with only `python`
- a document with only `search`
- a document with only `database`
- a document that should be excluded because it contains `database`

Boolean search fixes that:

```text
AFTER: boolean search applies AND, OR, and NOT logic
FILE_NAME: python_search.txt
MATCHED_TERMS: python, search
EXCLUDED_TERMS: database
```

That is the improvement.

The result is not just matching words.

It is satisfying the query logic.

## Demo Data

Use this controlled corpus:

```python
BOOLEAN_DEMO_QUERY = "python AND search NOT database"

BOOLEAN_DEMO_DOCUMENTS = {
    "python_search.txt": "python search engine tutorial",
    "python_database.txt": "python database search indexing",
    "search_only.txt": "search ranking bm25",
    "python_only.txt": "python scripting automation",
    "database_only.txt": "database indexing tutorial",
}
```

This example is useful because every document teaches a different case:

- `python_search.txt` should match.
- `python_database.txt` has `python` and `search`, but must be removed because it has `database`.
- `search_only.txt` is missing `python`.
- `python_only.txt` is missing `search`.
- `database_only.txt` only has the excluded term.

## Set Operations

Boolean search is easy to explain using sets.

The inverted index already gives us this:

```text
python -> {python_search.txt, python_database.txt, python_only.txt}
search -> {python_search.txt, python_database.txt, search_only.txt}
database -> {python_database.txt, database_only.txt}
```

Now apply Boolean operators.

### AND

`AND` means intersection.

```text
python AND search
```

means:

```text
documents_with_python intersection documents_with_search
```

Result:

```text
{python_search.txt, python_database.txt}
```

### OR

`OR` means union.

```text
python OR database
```

means:

```text
documents_with_python union documents_with_database
```

Result:

```text
{database_only.txt, python_database.txt, python_only.txt, python_search.txt}
```

### NOT

`NOT` means difference.

```text
python AND search NOT database
```

means:

```text
(documents_with_python intersection documents_with_search) minus documents_with_database
```

Result:

```text
{python_search.txt}
```

## Implementation

First, parse the query:

```python
def parse_boolean_query(query: str) -> list[str]:
    result = []
    for token in re.findall(r"[a-zA-Z]+", query):
        upper_token = token.upper()
        if upper_token in BOOLEAN_OPERATORS:
            result.append(upper_token)
        else:
            result.append(token.lower())
    return result
```

For this tutorial, operators are written as words:

```text
AND
OR
NOT
```

Then evaluate the query with precedence:

```text
NOT first
AND second
OR third
```

That means:

```text
python OR database AND search
```

is interpreted as:

```text
python OR (database AND search)
```

not:

```text
(python OR database) AND search
```

The core idea is:

```python
AND -> result = left_set & right_set
OR  -> result = left_set | right_set
NOT -> result = all_documents - term_set
```

Then the public helper is:

```python
def boolean_search(query: str, fileData: dict[str, str]) -> list[dict]:
    inverted_index = build_inverted_index(fileData)
    return search_boolean(query, inverted_index, set(fileData.keys()))
```

This keeps the video simple.

The demo can call one function:

```python
boolean_search("python AND search NOT database", BOOLEAN_DEMO_DOCUMENTS)
```

## Operator Examples

### AND narrows

```text
QUERY: python AND search
FILE_NAME: python_database.txt
MATCHED_TERMS: python, search
FILE_NAME: python_search.txt
MATCHED_TERMS: python, search
```

Both documents contain both required terms.

### OR broadens

```text
QUERY: python OR database
FILE_NAME: database_only.txt
MATCHED_TERMS: database
FILE_NAME: python_database.txt
MATCHED_TERMS: python, database
FILE_NAME: python_only.txt
MATCHED_TERMS: python
FILE_NAME: python_search.txt
MATCHED_TERMS: python
```

Any document with either term can match.

### NOT excludes

```text
QUERY: python AND search NOT database
FILE_NAME: python_search.txt
MATCHED_TERMS: python, search
EXCLUDED_TERMS: database
```

The database document is removed.

## Why Boolean Search Is Useful

Boolean search is useful when the user wants control.

Examples:

```text
python AND django
```

means the result must mention both.

```text
java OR kotlin
```

means either language is acceptable.

```text
apple NOT fruit
```

means remove fruit-related results.

This is useful in:

- documentation search
- legal search
- log search
- research databases
- recruiting search
- support-ticket search

Boolean search is especially useful when the user knows exactly what they want to include and exclude.

## Where Boolean Search Fails

Boolean search is strict.

That is both the benefit and the weakness.

It can fail when:

- the user chooses the wrong term
- the document uses a synonym
- spelling or stemming matters
- the query is too restrictive
- `NOT` removes useful documents
- the user expects ranking, but Boolean search only filters

Example:

```text
python AND search NOT database
```

will remove:

```text
python database search indexing
```

That is correct logically.

But maybe that document was still useful.

So Boolean search is not always better than BM25.

It solves a different problem.

## Ranking Tradeoff

BM25 gives scores.

Boolean search gives a matching set.

So Boolean search answers:

```text
Should this document be included?
```

BM25 answers:

```text
How high should this document rank?
```

In real search engines, these are often combined.

For example:

```text
filter with Boolean search
rank the remaining documents with BM25
```

That gives you precision from Boolean logic and ranking from BM25.

## Closing

Day 13 adds explicit query logic.

Now the search engine understands:

```text
AND = must include both
OR = can include either
NOT = must exclude this term
```

This moves the engine from loose keyword matching to controlled search.
