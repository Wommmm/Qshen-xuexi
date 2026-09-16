from pymilvus import MilvusClient
def danse_vector_search(client:MilvusClient,collenction_name:str,query_vecotor:list,top_k:list):
    """
    基于稠密向量进行搜索
    """
    res = client.search(
        collection_name=collenction_name,
        data=[query_vecotor],
        anns_field="vector",
        limit=top_k，
        metric_type="COSINE"
    )
    if res:
        result = res[0]
        print(result)

client = MilvusClient(url="http://127.0.0.1:19530")
query = "国家所有权"
from FlagEmbedding import BGEM3FlagModel    
model = BGEM3FlagModel(r"D:\LANGCHANINDEMO\assets\models\bge-m3")
query_vecotor = model.encode([query],return_dense=True,return_sparse=True)
danse_vec = query_vecotor["dense_vecs"][0]
danse_vector_search(client,collenction_name="demo_collection",query_vecotor=query_vecotor,top_k=1)
