# Milvus 向量检索示例代码
# 功能：演示稠密向量检索和混合检索（稠密+稀疏）的实现

from pymilvus import MilvusClient

def danse_vector_search(client:MilvusClient, collenction_name:str, query_vecotor:list, top_k:list):
    """
    基于稠密向量进行搜索
    
    参数说明:
        client: Milvus 客户端实例
        collenction_name: 集合名称
        query_vecotor: 查询向量（稠密向量）
        top_k: 返回最相似的 top_k 个结果
    """
    # 调用 Milvus 的 search 方法进行向量检索
    res = client.search(
        collection_name=collenction_name,
        data=[query_vecotor],           # 查询数据，需要是列表格式
        anns_field="vector",            # 指定向量字段名称
        limit=top_k,                    # 返回结果数量限制
        metric_type="COSINE",           # 使用余弦相似度作为距离度量方式
        output_fields=["text"]          # 指定需要返回的非向量字段
    )
    if res:
        result = res[0]                 # 取第一个查询结果
        print(result)

def hybrid_search(client:MilvusClient, collenction_name:str, danse_vec:list, query_sparse_vecotor:dict, top_k:int):
    """
    基于稠密向量和稀疏向量进行混合检索
    
    参数说明:
        client: Milvus 客户端实例
        collenction_name: 集合名称
        danse_vec: 稠密向量
        query_sparse_vecotor: 稀疏向量（字典格式）
        top_k: 返回最相似的 top_k 个结果
        
    
    返回:
        混合检索结果
    """
    # 1. 引入 Milvus 当中的 AnnSearchRequest 类，用于构建 ANN（近似最近邻）搜索请求
    from pymilvus import AnnSearchRequest

    # 2. 创建 AnnSearchRequest 对象：分别构建稠密向量检索和稀疏向量检索请求
    # 稠密向量检索请求
    danse_request = AnnSearchRequest(
            data=[danse_vec],           # 稠密向量数据
            anns_field="vector",        # 向量字段名
            limit=top_k,                # 返回结果数量
            param={"metric_type":"COSINE"},  # 使用余弦相似度
        )
    # 稀疏向量检索请求
    sparse_request = AnnSearchRequest(
        data=[query_sparse_vecotor],    # 稀疏向量数据（字典格式）
        anns_field="sparse_vector",     # 稀疏向量字段名
        limit=top_k,                    # 返回结果数量
        param={"metric_type":"IP"},     # 使用内积（Inner Product）作为度量方式
    )
    
    # 3. 构造混合检索的 reranker 对象：RRFRanker（倒数排序融合）
    # RRF 是一种常用的结果融合算法，可以合并多路检索结果
    from pymilvus import RRFRanker
    reranker = RRFRanker()
    
    # 4. 通过调用 client.hybrid_search() 方法进行混合检索
    res = client.hybrid_search(
        collection_name=collenction_name,
        reqs=[sparse_request, danse_request],  # 传入多个搜索请求
        ranker=reranker,                       # 使用 RRF 融合排序
        limit=top_k, # 返回结果数量
        output_fields = ["text"]# 指定需要返回的非向量字段
                                                      
    )
    return res

# ==================== 主程序 ====================

# 1. 创建 Milvus 客户端，连接到本地 Milvus 服务
client = MilvusClient(uri="http://127.0.0.1:19530")

# 2. 定义查询文本
query = "国家所有权是在第几章规定的"

# 3. 加载 BGE-M3 模型（支持同时输出稠密向量和稀疏向量）
from FlagEmbedding import BGEM3FlagModel    
model = BGEM3FlagModel(r"D:\LANGCHANINDEMO\assets\models\bge-m3")

# 4. 对查询文本进行编码，同时获取稠密向量和稀疏向量
result = model.encode([query], return_dense=True, return_sparse=True)
danse_vec = result["dense_vecs"][0].tolist()      # 稠密向量：用于语义相似度匹配
sparse_vec = result["lexical_weights"][0]          # 稀疏向量：用于关键词精确匹配

# 5. 执行稠密向量检索
danse_vector_search(client, collenction_name="demo_collection", query_vecotor=danse_vec, top_k=1)
print(danse_vector_search)

# 6. 执行混合检索（结合稠密向量和稀疏向量）
res = hybrid_search(client, "demo_collection", danse_vec=danse_vec, query_sparse_vecotor=sparse_vec,top_k=3,)
# print(res[0])  # 打印第一个查询结果
# print(res)     # 打印完整结果

# # 7. 查看集合的字段信息
# for f in client.describe_collection("demo_collection")["fields"]:
#     print(f["name"], f["type"], f.get("params"))

#8.生成
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

texts = [hit["entity"]["text"] for hit in res[0]]
context = "\n\n".join(texts)

message_list = [
    {"role": "system",
     "content": "你是一个专业的法律问答机器人，只能根据提供的上下文回答问题；如果上下文无法回答，就回答「根据上下文无法回答该问题」"},
    {"role": "user",
     "content": f"根据以下上下文回答问题：\n{context}\n\n问题：{query}"},
]

llm = ChatOpenAI(model="deepseek-chat")
print(llm.invoke(message_list).content)