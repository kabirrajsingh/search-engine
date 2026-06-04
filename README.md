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

BM25 Ranking
- upgrade an TF-iDF
- If a document repeats a matching word many times, TF-IDF continues giving weight to that repetition

BM25
- Term frequeny saturation
- Document length normalization


TF-IDF = term_frequency * inverse_document_frequency

- still cares about term frequency
- but it does not let term frequency grow forever
- the first few repetitions help. but after that each extra repetition is less valuable
this is term frequency saturation

- BM25 also checks the document length
- if a document is very long. it has more chances to accidentally match query words. BM25 normalizes this.
This is document length normalization

BM25 formula
score= idf * ((tf * (k1+1)) / (tf+ k1 * (1 - b + b * (doc_length/avg_doc_length))))

The pieces are
- tf: how many times the term appears in the document
- idf: how rare is the term across documents
- doc_length: number of tokens in this document
- avg_doc_length : average document length in the corpus
- k1: controls term frequency saturation (1.5)
- b: controls document length normalization (0.75)


car
automobile

not recommended
do not recommend me

machine learning != machine .... learning

Normal search -> Does this document contain the query words?

Phrase search -> Do these query words appear next ot each other in this exact order?
