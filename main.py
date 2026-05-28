import os
import re
import time
def tokenize(query:str) -> list[str]:
    return re.findall(r"[a-zA-Z]+",query.lower())

def load_files(path: str) -> dict[str,str]:
    fileNames=os.listdir(path)
    fileData={}
    for file in fileNames:
        full_path=os.path.join(path,file)
        if os.path.isfile(full_path):
            with open(full_path,"r",encoding="utf-8") as f:
                fileData[file]= f.read()

    return fileData


def basic_search(query: str,fileData: dict[str,str]) -> list[str]:
    tokens=set(tokenize(query))
    res=[]
    for fileName,file in fileData.items():
        tokenized_file_data=set(tokenize(file))
        # tokens in the query
        # tokens in fileData
        if(tokenized_file_data & tokens):
            res.append(fileName)
    return res

def build_inverted_index(fileData: dict[str,str]) -> dict[str,set[str]]:
    result={}
    for file_name,file_content in fileData.items():
        tokens=set(tokenize(file_content))
        for token in tokens:
            if token not in result:
                result[token]=set()
            result[token].add(file_name)
    return result

def search_inverted_index( query: str,invertedIndex: dict[str,set[str]] ) -> list[str]:
    tokens=set(tokenize(query))
    result_set=[]
    for token in tokens:
        doc_set=invertedIndex.get(token,set())
        result_set.append(doc_set)
    return list(set.union(*result_set))

def measure_time(func, *args):
    start=time.perf_counter()
    result=func(*args)
    end=time.perf_counter()
    return result,end-start

def main():
    file_details=load_files("data")
    
    inverted_index=build_inverted_index(file_details)
    query=" Computer programming course computer"
    queries= [
        "recommendation systems",
        "neural networks",
        "tcp ip protocol",
        "database normalization",
        "indexing in sql",
        "operating system scheduling",
        "deadlock prevention",
    ]
    search_methods={
        "basic":lambda q:basic_search(q,file_details),
        "inverted_index": lambda q: search_inverted_index(q, inverted_index)
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
            # print(f"RESULTS : {results}")
            print("-"*50)
        
    # for result in results:
    #     print(result)
        

    # result,time=measure_time(basic_search,query,fileData)
    # print(result)
    # print(time)
    # result,time2=measure_time(search_inverted_index,invertedIndex,query)
    # print(result)
    # print(time2)

if __name__=="__main__":
    main()