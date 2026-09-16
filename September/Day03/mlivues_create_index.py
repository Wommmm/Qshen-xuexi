
from pymilvus import MilvusClient

client = MilvusClient(uri="tcp://127.0.0.1:19530", token="")

index_params = MilvusClient.prepare_index_params()
index_params.add_index(field_name="vector", index_type="HNSW", metric_type="COSINE")
index_params.add_index(field_name="sparse_vector",
                       index_type="SPARSE_INVERTED_INDEX", metric_type="IP")
client.create_index("demo_collection", index_params)
print("索引创建完成")