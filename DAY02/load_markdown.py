def markown_loader_demo():
    from langchain_community.document_loaders import UnstructuredMarkdownLoader

    file_path= r"lianxineir\sample.md"
    loader = UnstructuredMarkdownLoader(
        file_path=file_path,
        mode="elements",
    )
    document = loader.load()
    print(document[0])

from typing import List
from langchain_core.documents import Document

def enrich_document_info(document_list:List[Document]):
    #维护一个栈，用来存放历史的标题
    stack=[]
    category_depth = 0
    for doc in document_list:
        if doc.metadata["category"] == 'Title':
            