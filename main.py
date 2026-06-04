from search_engine.searchengine import basic_search, build_bm25_index, build_inverted_index, build_ranked_inverted_index, build_tfidf_index, check_file_exists, phrase_search, read_index, save_index, search_bm25_index, search_bm25_index_with_snippets, search_inverted_index, search_ranked_inverted_index, search_ranked_inverted_index_with_snippets, search_tfidf_index, search_tfidf_index_with_snippets, search_bm25_index_with_explanation
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
    bm25_index=build_bm25_index(file_details)
    search_methods={
        # "basic":lambda q:basic_search(q,file_details),
        # "inverted_index": lambda q: search_inverted_index(q, inverted_index),
        # "ranked_inverted_index": lambda q:search_ranked_inverted_index(q,ranked_inverted_index),
        # "ranked_inverted_index_with_snippets": lambda q:search_ranked_inverted_index_with_snippets(q,ranked_inverted_index,file_details),
        "tfidf_index_search": lambda q:search_tfidf_index(q,tfidf_index),
        "tfidf_index_search": lambda q:search_tfidf_index_with_snippets(q,tfidf_index,file_details),
        "bm25_index_search":  lambda q:search_bm25_index(q,bm25_index),
        "bm25_index_search": lambda q:search_bm25_index_with_snippets(q,bm25_index,file_details),
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


BM25_DEMO_QUERY="nlp retrieval"
BM25_DEMO_DOCUMENTS ={
    "keyword_stuffed_nlp.txt":"nlp nlp nlp nlp nlp nlp nlp",
    "relevant_nlp_retrieval.txt":"nlp retrieval search ranking",
    "background_retrieval.txt":"retrieval database indexing"
}



PHRASE_SEARCH="machine learning"
PHRASE_DEMO_DOCUMENTS={
    "exact_machine_learning.txt":"machine learning phrase improves search ranking",
    "repeated_words.txt":"machine learning models use machine learning data",
    "seperate_words.txt":"machine system improve learning outcomes",
    "reversed_words.txt":" learning machine behavior is not the same phrase"
}

def print_explainable_result(result:dict):
    print(f"FILE_NAME: {result['file_name']}")
    print(f"FINAL_SCORE: {result['score']}")
    print(f"MATCHED TERMS")    
    for term in result["matched_terms"]:
        print(
            f"   {term['term']}  ->"
            f"tf={term['term_frequency']},"
            f"df={term['document_frequency']},",
            f"idf={term['idf']},"
            f"saturated_tf={term['saturated_tf']},"
            f"contribution={term['contribution']},"
        )
    if result["unmatched_terms"]:
        print(f"unmatched_terms: {','.join(result['unmatched_terms'])}")
    contribution_total=sum(term["contribution"] for term in result["matched_terms"])
    print(f" SCORE_CHECK: {round(contribution_total,4)} from matched term terms")

def show_demo_without_tfidf():
    ranked_inverted_index=load_or_build_ranked_index(TFIDF_DEMO_DOCUMENTS)
    print(search_ranked_inverted_index_with_snippets(TFIDF_DEMO_QUERY,ranked_inverted_index,TFIDF_DEMO_DOCUMENTS))

def show_demo_with_tfidf():
    tfidf_index=build_tfidf_index(TFIDF_DEMO_DOCUMENTS)
    print(search_tfidf_index(TFIDF_DEMO_QUERY,tfidf_index))

def show_demo_without_bm25():
    tfidf_index=build_tfidf_index(BM25_DEMO_DOCUMENTS)
    print(search_tfidf_index(BM25_DEMO_QUERY,tfidf_index))

def show_demo_with_bm25():
    bm25_index=build_bm25_index(BM25_DEMO_DOCUMENTS)
    print(search_bm25_index(BM25_DEMO_QUERY,bm25_index))


def phrase_search_demo():
    phrase_search_output=phrase_search(PHRASE_SEARCH,PHRASE_DEMO_DOCUMENTS)
    for result in phrase_search_output:
        print(result)

def show_demo_with_bm25_explanations():
    bm25_index=build_bm25_index(BM25_DEMO_DOCUMENTS)
    explainable_results=search_bm25_index_with_explanation(BM25_DEMO_QUERY,bm25_index,BM25_DEMO_DOCUMENTS)
    for result in explainable_results:
        print(result)
        print("*" * 50)

def main():
    file_details=load_files("data")
    # run_method_comparison(file_details)
    # show_demo_with_bm25_explanations()
    phrase_search_demo()

if __name__=="__main__":
    main()