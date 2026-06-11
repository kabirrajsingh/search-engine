import argparse
from pathlib import Path

from search_engine.searchengine import (
    basic_search,
    build_bm25_index,
    build_ranked_inverted_index,
    build_tfidf_index,
    phrase_search,
    search_bm25_index_with_snippets,
    search_ranked_inverted_index_with_snippets,
    search_tfidf_index_with_snippets,
)


SEARCH_MODES=("basic","ranked","tfidf","bm25","phrase")


def load_files(path: str) -> dict[str,str]:
    data_path=Path(path)
    if not data_path.exists():
        raise FileNotFoundError(f"Data path does not exist: {path}")
    if not data_path.is_dir():
        raise NotADirectoryError(f"Data path is not a directory: {path}")

    file_data={}
    for file_path in sorted(data_path.iterdir()):
        if file_path.is_file():
            file_data[file_path.name]=file_path.read_text(encoding="utf-8")

    if not file_data:
        raise ValueError(f"No readable files found in: {path}")

    return file_data


def run_search(query:str,file_data:dict[str,str],mode:str="bm25") -> list[dict]:
    if mode == "basic":
        return basic_search(query,file_data)
    if mode == "ranked":
        ranked_index=build_ranked_inverted_index(file_data)
        return search_ranked_inverted_index_with_snippets(query,ranked_index,file_data)
    if mode == "tfidf":
        tfidf_index=build_tfidf_index(file_data)
        return search_tfidf_index_with_snippets(query,tfidf_index,file_data)
    if mode == "bm25":
        bm25_index=build_bm25_index(file_data)
        return search_bm25_index_with_snippets(query,bm25_index,file_data)
    if mode == "phrase":
        return phrase_search(query,file_data)

    raise ValueError(f"Unsupported search mode: {mode}")


def format_results(results:list[dict],limit:int=5) -> str:
    if not results:
        return "NO RESULTS"

    lines=[]
    for result in results[:limit]:
        lines.append(f"FILE_NAME: {result['file_name']}")
        if "score" in result:
            lines.append(f"SCORE: {round(result['score'],4)}")
        if "phrase_count" in result:
            lines.append(f"PHRASE_COUNT: {result['phrase_count']}")
        if "snippet" in result and result["snippet"]:
            lines.append("SNIPPETS:")
            for snippet in result["snippet"]:
                lines.append(snippet)
        lines.append("-"*50)

    return "\n".join(lines).rstrip("-"*50).rstrip()


def build_parser() -> argparse.ArgumentParser:
    parser=argparse.ArgumentParser(
        prog="search-engine",
        description="Run the tutorial search engine from the command line."
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="operating system scheduling",
        help="Query text to search for."
    )
    parser.add_argument(
        "--data",
        default="data",
        help="Directory containing text files to search."
    )
    parser.add_argument(
        "--mode",
        choices=SEARCH_MODES,
        default="bm25",
        help="Search mode to run."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of results to print."
    )
    return parser


def main(argv:list[str] | None=None) -> int:
    parser=build_parser()
    args=parser.parse_args(argv)

    file_data=load_files(args.data)
    results=run_search(args.query,file_data,args.mode)

    print("SEARCH ENGINE CLI")
    print(f"MODE: {args.mode}")
    print(f"QUERY: {args.query}")
    print("-"*50)
    print(format_results(results,args.limit))
    return 0
