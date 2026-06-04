import math
import os
import re
import json
from stopwords import get_stopwords

STOPWORDS: list[str]=get_stopwords("english")

def tokenize(query:str) -> list[str]:
    return re.findall(r"[a-zA-Z]+",query.lower())


def tokenize_with_stopwords(query:str , stopwords:set[str]) -> list[str]:
    return [token for token in tokenize(query)
            if token not in stopwords]


def calculate_idf(total_docs,frequency) -> float:
    if(total_docs) <= 0:
        return 0.0
    return math.log((total_docs+1)/(frequency+1))


def calculate_bm25_idf(total_docs:int, document_frequency:int) -> float:
    if total_docs <=0 or document_frequency <=0 :
        return 0.0
    return math.log(1 + ((total_docs - document_frequency + 0.5)/(document_frequency + 0.5)))

def calculate_document_lengths(fileData:dict[str,str]) -> dict[str,int]:
    return{
        file_name:len(tokenize_with_stopwords(file_content,STOPWORDS))
        for file_name, file_content in fileData.items()
    }

def calculate_bm25_length_normalizer(document_length,average_document_length,b) -> float:
    if(average_document_length<=0):
        return 0.0
    return  1 - b + b * (document_length/average_document_length)


def calculate_bm25_satured_tf(term_frequency,length_normalizer,k1):
    return (term_frequency * (k1+1)) / (term_frequency + k1 * length_normalizer) 

def calculate_bm25_term_contribution(term_frequency,idf,document_length,average_document_length,k1,b) -> float:
        length_normalizer =calculate_bm25_length_normalizer(document_length,average_document_length,b)  
        saturated_tf = calculate_bm25_satured_tf(term_frequency,length_normalizer,k1) 
        return idf * saturated_tf

def build_bm25_index(fileData:dict[str,str],k1:float=1.5,b:float=0.75) -> dict[str,dict[str,float]]:
    ranked_index=build_ranked_inverted_index(fileData)
    document_lengths = calculate_document_lengths(fileData)
    average_document_length=calculate_average_document_lengths(document_lengths)
    total_docs=len(fileData)

    result={}

    for token,document_counts in ranked_index.items():
        idf=calculate_bm25_idf(total_docs,len(document_counts))
        result[token] ={}
        for file_name, term_frequency in document_counts.items():
            document_length=document_lengths[file_name]
            result[token][file_name]=calculate_bm25_term_contribution(term_frequency,idf,document_length,average_document_length,k1,b)
    return result

def explain_bm25_result(query:str,file_name:str, bm25_index:dict[str,dict[str,float]],file_data:dict[str,str],k1:float=1.5,b:float=0.75) -> dict:
    query_tokens=tokenize_with_stopwords(query,STOPWORDS)
    ranked_index=build_ranked_inverted_index(file_data)
    document_lengths=calculate_document_lengths(file_data)
    average_document_lengths=calculate_average_document_lengths(document_lengths)
    total_docs=len(file_data)
    document_length=document_lengths.get(file_name,0)
    matched_terms=[]
    unmatched_terms=[]
    raw_score=0.0
    for token in query_tokens:
        document_counts=ranked_index.get(token,{})
        term_frequency=document_counts.get(file_name,0)
        if term_frequency <= 0:
            unmatched_terms.append(token)
            continue
        document_frequency=len(document_counts)
        idf=calculate_bm25_idf(total_docs,document_frequency)
        length_normalizer=calculate_bm25_length_normalizer(document_length,average_document_lengths,b)
        saturated_tf=calculate_bm25_satured_tf(term_frequency,length_normalizer,k1)
        contribution=bm25_index.get(token,{}).get(file_name)
        if contribution is None:
            contribution=idf * saturated_tf
        raw_score+=contribution
        matched_terms.append({
            "term":token,
            "term_frequency":term_frequency,
            "document_frequency":document_frequency,
            "idf":idf,
            "document_length":document_length,
            "average_document_lengths":average_document_lengths,
            "length_normalizer":length_normalizer,
            "saturated_tf":saturated_tf,
            "contribution":contribution
        })
    return {
        "file_name":file_name,
        "score":raw_score,
       " matched_terms":matched_terms,
        "unmatched_terms": unmatched_terms,
        "score_explanation": " BM25 score is the sum of each matched query term contribution"
    }

def search_bm25_index_with_explanation(query:str, bm25_index:dict[str,dict[str,float]],file_data:dict[str,str],k1:float=1.5,b:float=0.75) -> list[dict]:
    ranked_docs=search_bm25_index(query,bm25_index)
    return [
        explain_bm25_result(query,result['file_name'],bm25_index,file_data,k1,b) for result in ranked_docs
    ]
    
def calculate_average_document_lengths(document_lengths: dict[str,int]) -> float:
    if not document_lengths:
        return 0.0
    return sum(document_lengths.values()) / len(document_lengths)



def search_bm25_index(query:str, bm25_index:dict[str,dict[str,float]]) -> list[dict]:
    tokens=set(tokenize_with_stopwords(query,STOPWORDS))
    scores:dict[str,float]={}
    for token in tokens:
        doc_set=bm25_index.get(token,{})
        for file_name,weight in doc_set.items():
            if weight <= 0:
                continue
            if file_name not in scores:
                scores[file_name]=0
            scores[file_name]+=weight

    ranked_docs=sorted(
        scores.items(),
        key= lambda x: (-x[1],x[0])
    )
    return [{"file_name":doc,"score":round(score,4)} for doc,score in ranked_docs]


def search_bm25_index_with_snippets( query: str,bm25_index:  dict[str,dict[str,float]],file_data:dict[str,str]) -> list[dict]:
    results=[]
    tokens=set(tokenize_with_stopwords(query,STOPWORDS))
    scores:dict[str,float]={}
    for token in tokens:
        doc_set=bm25_index.get(token,{})
        for file_name,weight in doc_set.items():
            if weight <= 0:
                continue
            if file_name not in scores:
                scores[file_name]=0
            scores[file_name]+=weight

    ranked_docs=sorted(
        scores.items(),
        key= lambda x: (-x[1],x[0])
    )
    for file_name,score in ranked_docs:
        snippet=create_snippet(file_data[file_name],tokens)
        results.append({
            "file_name":file_name,
            "score":score,
            "snippet":snippet
        })
    return results

def build_tfidf_index(fileData:dict[str,str])-> dict[str,dict[str,float]]:
    ranked_index=build_ranked_inverted_index(fileData)
    total_docs=len(fileData)
    result={}
    for token,document_counts in ranked_index.items():
        idf=calculate_idf(total_docs,len(document_counts))
        result[token]={}
        for file_name,term_frequency in document_counts.items():
            result[token][file_name]=term_frequency*idf
    return result

def search_tfidf_index_with_snippets( query: str,tfidf_index:  dict[str,dict[str,float]],file_data:dict[str,str]) -> list[dict]:
    results=[]
    tokens=set(tokenize_with_stopwords(query,STOPWORDS))
    scores:dict[str,float]={}
    for token in tokens:
        doc_set=tfidf_index.get(token,{})
        for file_name,weight in doc_set.items():
            if weight <= 0:
                continue
            if file_name not in scores:
                scores[file_name]=0
            scores[file_name]=weight

    ranked_docs=sorted(
        scores.items(),
        key= lambda x: (-x[1],x[0])
    )
    for file_name,score in ranked_docs:
        snippet=create_snippet(file_data[file_name],tokens)
        results.append({
            "file_name":file_name,
            "score":score,
            "snippet":snippet
        })
    return results


def search_tfidf_index(query:str, tfidf_index:dict[str,dict[str,float]]) -> list[dict]:
    tokens=set(tokenize_with_stopwords(query,STOPWORDS))
    scores:dict[str,float]={}
    for token in tokens:
        doc_set=tfidf_index.get(token,{})
        for file_name,weight in doc_set.items():
            if weight <= 0:
                continue
            if file_name not in scores:
                scores[file_name]=0
            scores[file_name]=weight

    ranked_docs=sorted(
        scores.items(),
        key= lambda x: (-x[1],x[0])
    )
    return [{"file_name":doc,"score":round(score,4)} for doc,score in ranked_docs]


def basic_search(query: str,fileData: dict[str,str]) -> list[dict]:
    tokens=set(tokenize_with_stopwords(query,STOPWORDS))
    res=[]
    for fileName,file in fileData.items():
        tokenized_file_data=set(tokenize_with_stopwords(file,STOPWORDS))
        # tokens in the query
        # tokens in fileData
        if(tokenized_file_data & tokens):
            res.append(fileName)
    return [{"file_name":file_name} for file_name in res]

def build_inverted_index(fileData: dict[str,str]) -> dict[str,set[str]]:
    result={}
    for file_name,file_content in fileData.items():
        tokens=set(tokenize_with_stopwords(file_content,STOPWORDS))
        for token in tokens:
            if token not in result:
                result[token]=set()
            result[token].add(file_name)
    return result

def build_ranked_inverted_index(
    fileData: dict[str, str]
) -> dict[str, dict[str, int]]:
    result = {}

    for file_name, file_content in fileData.items():
        tokens = tokenize_with_stopwords(file_content, STOPWORDS)

        for token in tokens:
            result.setdefault(token, {})
            result[token][file_name] = result[token].get(file_name, 0) + 1

    return result

def search_inverted_index( query: str,invertedIndex: dict[str,set[str]] ) -> list[dict]:
    tokens=set(tokenize_with_stopwords(query,STOPWORDS))
    result_set=[]
    for token in tokens:
        doc_set=invertedIndex.get(token,set())
        result_set.append(doc_set)
    results=list(set.union(*result_set))
    return [{"file_name":file_name} for file_name in results]

def search_ranked_inverted_index( query: str,ranked_inverted_index: dict[str,dict[str,int]] ) -> list[dict]:
    tokens=set(tokenize_with_stopwords(query,STOPWORDS))
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
    tokens=set(tokenize_with_stopwords(query,STOPWORDS))
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