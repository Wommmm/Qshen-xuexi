def load_word_demo():
    from langchain_community.document_loaders import UnstructuredWordDocumentLoader
    docx_loader = UnstructuredWordDocumentLoader(
        file_path=r"D:\LANGCHANINDEMO\lianxineir\sample.docx",
        mode="elements"
    )
    # 调用loader当中的load()方法
    document_list = docx_loader.load()

    for doc in document_list:
        print("doc的元数据信息:")
        print(doc.metadata)
        print("doc的问你本内容字符串")
        print(doc.page_content)
        print("="*50)
if __name__=="__main__":         
 load_word_demo()
