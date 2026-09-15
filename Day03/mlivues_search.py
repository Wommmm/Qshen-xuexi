from pymilvus import MilvusClient
def danse_vector_search(client:MilvusClient,collenction_name:str,query_vecotor:list,top_k:list):
    """
    基于稠密向量进行搜索
    """
    client.search(
        collection_name=collenction_name,
        data=[query_vecotor],
        anns_field="vector",
        limit=top_k
    )