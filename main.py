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

def build_ranked_inverted_index(fileData: dict[str,str]) -> dict[str,dict[str,int]]:
    result={}
    for file_name,file_content in fileData.items():
        tokens=tokenize(file_content)
        for token in tokens:
            if token not in result:
                result[token]={}
            if file_name not in result[token]:
                result[token][file_name]=1
            else:
                result[token][file_name]+=1
    return result

def search_inverted_index( query: str,invertedIndex: dict[str,set[str]] ) -> list[str]:
    tokens=set(tokenize(query))
    result_set=[]
    for token in tokens:
        doc_set=invertedIndex.get(token,set())
        result_set.append(doc_set)
    return list(set.union(*result_set))

def search_ranked_inverted_index( query: str,ranked_inverted_index: dict[str,dict[str,int]] ) -> list[str]:
    tokens=set(tokenize(query))
    scores: dict[str,int]={}
    for token in tokens:
        doc_set=ranked_inverted_index.get(token,{})
        for file_name,count in doc_set.items():
            if file_name not in scores:
                scores[file_name]=0
            scores[file_name]+=count

    ranked_docs=sorted(
        scores.items(),
        key= lambda x: x[1],
        reverse=True
    )
    return [doc for doc,score in ranked_docs]

def measure_time(func, *args):
    start=time.perf_counter()
    result=func(*args)
    end=time.perf_counter()
    return result,end-start

def main():
    file_details=load_files("data")
    
    inverted_index=build_inverted_index(file_details)
    ranked_inverted_index=build_ranked_inverted_index(file_details)
    print(ranked_inverted_index)
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
        # "basic":lambda q:basic_search(q,file_details),
        # "inverted_index": lambda q: search_inverted_index(q, inverted_index),
        "ranked_inverted_index": lambda q:search_ranked_inverted_index(q,ranked_inverted_index)
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
            print(f"RESULTS : {result}")
            print("-"*50)
        


if __name__=="__main__":
    main()