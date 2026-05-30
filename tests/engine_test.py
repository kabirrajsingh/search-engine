from main import measure_time
from search_engine.searchengine import basic_search, search_inverted_index, tokenize


def test_tokenize_lowercase_and_returns_letters():
    assert tokenize("Hello, WORLD! Python3 and AI ML 10") == [
        "hello",
        "world",
        "python",
        "and",
        "ai",
        "ml"
    ]

def test_basic_search_returns_documents_containing_any_query_tokens():
    file_data={
        "ai.txt":"Neural networks and machine learning",
        "db.txt":" SQL indexing and normalization",
        "empty.txt":" No matching topic here"
    }

    assert basic_search("learning sql",file_data) == ['ai.txt', 'db.txt']

def test_search_inverted_index_returns_union_of_matching_documents():
    index = {
        "python" : {"doc1.txt","doc2.txt"},
        "database": {"doc3.txt"}
    }

    assert set(search_inverted_index("python database", index)) == {"doc1.txt","doc2.txt","doc3.txt"}
    assert search_inverted_index("missing",index) == []

def test_measure_time_returns_function_result_and_elapsed_time():
    def add(a,b):
        return a+b
    result,elapsed = measure_time(add,2,3)
    assert(result) == 5
    assert(elapsed) > 0
