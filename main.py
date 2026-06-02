from search_engine.searchengine import basic_search, build_inverted_index, build_ranked_inverted_index, build_tfidf_index, check_file_exists, read_index, save_index, search_inverted_index, search_ranked_inverted_index, search_ranked_inverted_index_with_snippets, search_tfidf_index, search_tfidf_index_with_snippets
import os
import time

def load_files(path: str) -> dict[str,str]:
    fileNames=os.listdir(path)
    fileData={}
    for file in fileNames:
        full_path=os.path.join(path,file)
        if os.path.isfile(full_path):
            with open(full_path,"r",encoding="utf-8") as f:
                fileData[file]= f.read()

    return fileData

def measure_time(func, *args):
    start=time.perf_counter()
    result=func(*args)
    end=time.perf_counter()
    return result,end-start

INDEX_PATH="index_data.json"
SEARCH_QUERIES=[
        # "recommendation systems",
        # "neural networks",
        # "tcp ip protocol",
        # "database normalization",
        # "indexing in sql",
        "operating system scheduling",
        # "deadlock prevention",
    ]

def print_results(result: list[dict]):
    for item in result:
        print(f"FILE_NAME: {item['file_name']}")
        if 'score' in item:
            print(f"SCORE: {item['score']}")
        if 'snippet' in item:
            print("SNIPPETS:")
            for snippet in item['snippet']:
                print(f"{snippet}")



def load_or_build_ranked_index(file_details: dict[str,str]):
    if not check_file_exists(INDEX_PATH):
        ranked_inverted_index=build_ranked_inverted_index(file_details)
        save_index(ranked_inverted_index,INDEX_PATH)
        return ranked_inverted_index
    return read_index(INDEX_PATH)

def run_method_comparison(file_details: dict[str,str]):
    ranked_inverted_index=load_or_build_ranked_index(file_details)
    inverted_index=build_inverted_index(file_details)
    tfidf_index=build_tfidf_index(file_details)
    search_methods={
        # "basic":lambda q:basic_search(q,file_details),
        # "inverted_index": lambda q: search_inverted_index(q, inverted_index),
        # "ranked_inverted_index": lambda q:search_ranked_inverted_index(q,ranked_inverted_index),
        # "ranked_inverted_index_with_snippets": lambda q:search_ranked_inverted_index_with_snippets(q,ranked_inverted_index,file_details),
        "tfidf_index_search": lambda q:search_tfidf_index(q,tfidf_index),
        "tfidf_index_search": lambda q:search_tfidf_index_with_snippets(q,tfidf_index,file_details),
    }

    results=[]
    for search_method,search_fn in search_methods.items():
        current_time_taken=0
        for query in SEARCH_QUERIES:
            current_result=[]
            print(f"QUERY : {query}")
            result,time_taken=measure_time(search_fn,query)
            current_time_taken+=time_taken
            current_result.append(
                {
                    "method_name":search_method,
                    "result":result
                }
            )
            print(f"METHOD_NAME : {search_method}")
            print_results(result)

            print("-"*50)
        results.append({"method_name":search_method,"result":current_result,"time_taken": current_time_taken})

    print("*"*50)
    print("FINAL SUMMARY")
    for result in results:
        print(f"The time taken for method: {result["method_name"]} is {result["time_taken"]*100} ms")


TFIDF_DEMO_QUERY="system nlp"
TFIDF_DEMO_DOCUMENTS={
    "common_system_repetition.txt":"system system system system system system system system system maintainence",
    "nlp_doc.txt":"system nlp language model",
    "some_doc.txt":"system database indexing"
}

def show_demo_without_tfidf():
    ranked_inverted_index=load_or_build_ranked_index(TFIDF_DEMO_DOCUMENTS)
    print(search_ranked_inverted_index_with_snippets(TFIDF_DEMO_QUERY,ranked_inverted_index,TFIDF_DEMO_DOCUMENTS))

def show_demo_with_tfidf():
    tfidf_index=build_tfidf_index(TFIDF_DEMO_DOCUMENTS)
    print(search_tfidf_index(TFIDF_DEMO_QUERY,tfidf_index))

def main():
    file_details=load_files("data")
    run_method_comparison(file_details)

if __name__=="__main__":
    main()