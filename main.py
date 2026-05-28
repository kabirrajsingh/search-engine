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


def measure_time(func, *args):
    start=time.perf_counter()
    result=func(*args)
    end=time.perf_counter()
    return result,end-start

def main():
    fileData=load_files("data")
    query=" Computer programming course"
    result,time=measure_time(basic_search,query,fileData)
    print(result)
    print(time)


if __name__=="__main__":
    main()