from main import measure_time
from search_engine.cli import format_results, load_files, main as cli_main, run_search
from search_engine.searchengine import basic_search, search_inverted_index, tokenize


def result_file_names(results):
    return [result["file_name"] for result in results]


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

    assert basic_search("learning sql",file_data) == [
        {"file_name":"ai.txt"},
        {"file_name":"db.txt"}
    ]

def test_search_inverted_index_returns_union_of_matching_documents():
    index = {
        "python" : {"doc1.txt","doc2.txt"},
        "database": {"doc3.txt"}
    }

    assert set(result_file_names(search_inverted_index("python database", index))) == {
        "doc1.txt",
        "doc2.txt",
        "doc3.txt"
    }
    assert search_inverted_index("missing",index) == []

def test_cli_load_files_reads_text_files_from_directory(tmp_path):
    (tmp_path / "a.txt").write_text("python search",encoding="utf-8")
    (tmp_path / "b.txt").write_text("database indexing",encoding="utf-8")

    assert load_files(str(tmp_path)) == {
        "a.txt":"python search",
        "b.txt":"database indexing"
    }

def test_cli_run_search_supports_packaged_search_modes():
    file_data={
        "python_search.txt":"python search engine tutorial",
        "database.txt":"database indexing tutorial"
    }

    results=run_search("python search",file_data,"bm25")

    assert results[0]["file_name"] == "python_search.txt"
    assert "score" in results[0]

def test_cli_format_results_prints_result_fields():
    output=format_results([
        {
            "file_name":"python_search.txt",
            "score":1.23456,
            "snippet":["python search engine tutorial"]
        }
    ])

    assert "FILE_NAME: python_search.txt" in output
    assert "SCORE: 1.2346" in output
    assert "python search engine tutorial" in output

def test_cli_main_runs_with_temp_data_directory(tmp_path,capsys):
    (tmp_path / "python.txt").write_text("python search engine tutorial",encoding="utf-8")
    (tmp_path / "database.txt").write_text("database indexing",encoding="utf-8")

    exit_code=cli_main([
        "--data",
        str(tmp_path),
        "--mode",
        "basic",
        "python"
    ])
    output=capsys.readouterr().out

    assert exit_code == 0
    assert "SEARCH ENGINE CLI" in output
    assert "MODE: basic" in output
    assert "FILE_NAME: python.txt" in output

def test_measure_time_returns_function_result_and_elapsed_time():
    def add(a,b):
        return a+b
    result,elapsed = measure_time(add,2,3)
    assert(result) == 5
    assert(elapsed) > 0
