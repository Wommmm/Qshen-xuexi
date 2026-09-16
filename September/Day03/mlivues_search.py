from pymilvus import MilvusClient
def danse_vector_search(client:MilvusClient,collenction_name:str,query_vecotor:list,top_k:list):
    """
    基于稠密向量进行搜索
    """
    res = client.search(
        collection_name=collenction_name,
        data=[query_vecotor],
        anns_field="vector",
        limit=top_k,
        metric_type="COSINE",
        output_fields=["text"]
    )
    if res:
        result = res[0]
        print(result)

def hybrid_search(client:MilvusClient, collenction_name:str,danse_vec:list, query_sparse_vecotor:dict, top_k:int):
    """
    基于稠密向量和稀疏向量进行混合检索
    """
    #1.引入Milvues当中的AnnSearchRequest类
    from pymilvus import AnnSearchRequest

    #2.创建AnnSearchRequest对象:包含了稠密向量检索和稀疏向量检索
    danse_request = AnnSearchRequest(
            data=[danse_vec],
            anns_field="vector",
            limit=top_k,
            param={"metric_type":"COSINE"},
        )
    sparse_request = AnnSearchRequest(
        data=[query_sparse_vecotor],
        anns_field="sparse_vector",
        limit=top_k,
        param={"metric_type":"IP"},
    )
    #3.构造混合检索的reranker对象：RRFRanker
    from pymilvus import RRFRanker
    reranker = RRFRanker()
    #4.通过调用client.hybrid_search()方法进行混合检索
    res = client.hybrid_search(
        collection_name=collenction_name,
        reqs=[sparse_request,danse_request],
        ranker = reranker,
        limit = top_k,
    )
    return res

client = MilvusClient(uri="http://127.0.0.1:19530")
query = "国家所有权"
from FlagEmbedding import BGEM3FlagModel    
model = BGEM3FlagModel(r"D:\LANGCHANINDEMO\assets\models\bge-m3")
result = model.encode([query], return_dense=True, return_sparse=True)
danse_vec  = result["dense_vecs"][0].tolist()      # 稠密
sparse_vec = result["lexical_weights"][0]          # 稀疏 ← 新增这行
danse_vector_search(client,collenction_name="demo_collection",query_vecotor=danse_vec,top_k=1)
print(danse_vector_search)
#混合检索
res = hybrid_search(client, "demo_collection", danse_vec=danse_vec, query_sparse_vecotor=sparse_vec, top_k=3)
print(res[0]) 
print(res)
for f in client.describe_collection("demo_collection")["fields"]:
    print(f["name"], f["type"], f.get("params"))
