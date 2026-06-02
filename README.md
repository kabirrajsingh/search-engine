search-engine
- main.py
- search_engine
    - __init__.py, searchengine
- tests\
    - engine_test.py
- uv


uv run python main.py
uv run python -m pytest


Ranking will get serious
- Stopwords
- TF-IDF
- BM25
- Ranking Scores
- Phrase Search
- Boolean Search
- Packaging the app
- API UI etc....

TF-IDF -> Term Frequency- Inverse Document Frequency

IDF - How rare is this term across alol documents?

Final score= term_frequency* inverse_document_frequency

in our code= result[token][file_name] = term_frequency * idf

IDF= math.log((total_docs +1) / (document_frequency +1))