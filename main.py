from search_engine.searchengine import build_inverted_index, build_ranked_inverted_index, search_ranked_inverted_index_with_snippets
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


def main():
    file_details=load_files("data")
    
    inverted_index=build_inverted_index(file_details)
    ranked_inverted_index=build_ranked_inverted_index(file_details)
    query=" Computer programming course computer"
    queries= [
        "recommendation systems",
        # "neural networks",
        # "tcp ip protocol",
        # "database normalization",
        # "indexing in sql",
        # "operating system scheduling",
        # "deadlock prevention",
    ]
    search_methods={
        # "basic":lambda q:basic_search(q,file_details),
        # "inverted_index": lambda q: search_inverted_index(q, inverted_index),
        # "ranked_inverted_index": lambda q:search_ranked_inverted_index(q,ranked_inverted_index),
        "ranked_inverted_index_with_snippets": lambda q:search_ranked_inverted_index_with_snippets(q,ranked_inverted_index,file_details)
    }
    
    results=[]
    for query in queries:
        print(f"QUERY : {query}")
        for search_method,search_fn in search_methods.items():
            result,time_taken=measure_time(search_fn,query)
            results.append(
                {
                    "method_name":search_method,
                    "result":result,
                    "time_taken":time_taken
                }
            )
            print(f"METHOD_NAME : {search_method}")
            print(f"TIME_TAKEN : {time_taken}")
            for item in result:
                print(f"FILE_NAME: {item['file_name']}")
                print(f"SCORE: {item['score']}")
                print("SNIPPETS:")
                for snippet in item['snippet']:
                    print(f"{snippet}")
            print("-"*50)
        


if __name__=="__main__":
    main()