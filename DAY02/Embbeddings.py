def embedding_demo():
  """
  将文档切分成合适的大小之后，就可以使用嵌入模型生成文档的嵌入向量
  ，后续检索时用于与查询的嵌入向量进行相似度计算。
  """
  import os
  from langchain_huggingface import HuggingFaceEmbeddings
    #构建一个embed model
    #1.使用什么模型是否支持多语言
  embed_model = HuggingFaceEmbeddings(
        model_name=r'D:\LANGCHANINDEMO\assets\models\bge-base-zh-v1.5',
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
  #调用embed方法
  res = embed_model.embed_documents(['今天天气很好'])
  print(type(res[0]))
  print(len(res[0]))
   
if __name__=="__main__":  
  embedding_demo()