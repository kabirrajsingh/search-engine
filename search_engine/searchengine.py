import os
import re
import json
def tokenize(query:str) -> list[str]:
    return re.findall(r"[a-zA-Z]+",query.lower())

def basic_search(query: str,fileData: dict[str,str]) -> list[dict]:
    tokens=set(tokenize(query))
    res=[]
    for fileName,file in fileData.items():
        tokenized_file_data=set(tokenize(file))
        # tokens in the query
        # tokens in fileData
        if(tokenized_file_data & tokens):
            res.append(fileName)
    return [{"file_name":file_name} for file_name in res]

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

def search_inverted_index( query: str,invertedIndex: dict[str,set[str]] ) -> list[dict]:
    tokens=set(tokenize(query))
    result_set=[]
    for token in tokens:
        doc_set=invertedIndex.get(token,set())
        result_set.append(doc_set)
    results=list(set.union(*result_set))
    return [{"file_name":file_name} for file_name in results]

def search_ranked_inverted_index( query: str,ranked_inverted_index: dict[str,dict[str,int]] ) -> list[dict]:
    tokens=set(tokenize(query))
    scores: dict[str,int]={}
    results=[]
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
    return [{"file_name":doc,"score":score} for doc,score in ranked_docs]

def search_ranked_inverted_index_with_snippets( query: str,ranked_inverted_index: dict[str,dict[str,int]] ,file_data:dict[str,str]) -> list[dict]:
    tokens=set(tokenize(query))
    scores: dict[str,int]={}
    results=[]
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
    for file_name,score in ranked_docs:
        snippet=create_snippet(file_data[file_name],tokens)
        results.append({
            "file_name":file_name,
            "score":score,
            "snippet":snippet
        })
    return results

def create_snippet( content: str, query_tokens:set[str], max_snippets=3 , snippet_window=100) -> list[str]:
    lower_content=content.lower()
    snippets=[]
    start_pos=0
    for token in query_tokens:
        position=lower_content.find(token,start_pos)
        if(position==-1): continue
        start_pos=max(0,position-snippet_window // 2)
        end_pos= min(len(content),position+snippet_window //2)
        snippet=content[start_pos:end_pos]
        snippet=snippet.replace("\n"," ")
        snippets.append(snippet)
        start_pos=position+len(token)
    
    return snippets[:max_snippets]


def save_index(index_data:dict[str,set[str]],path: str):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(index_data,f)

def check_file_exists(path:str) -> bool:
    if(os.path.exists(path)):
        print(f"File already exists at {path}")
        return True
    return False

def read_index(path: str)-> dict[str,set[str]]:
    with open(path,"r",encoding="utf-8") as f:
        data=json.load(f)
    return data