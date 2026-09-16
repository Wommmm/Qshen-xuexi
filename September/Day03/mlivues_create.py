from pymilvus import DataType, MilvusClient

def get_client():
    # uri 必须带协议前缀（http/tcp 都可以）
    return MilvusClient(uri="tcp://127.0.0.1:19530", token="")

def build_schema():
    """
    定义集合结构，相当于关系型数据库里的 CREATE TABLE
    """
    schema = MilvusClient.create_schema()

    # 主键：INT64 类型，is_primary=True 表示这是主键
    schema.add_field(
        field_name="id",
        datatype=DataType.INT64,
        is_primary=True
    )

    # 稠密向量字段
    # 修改点 1：bge-m3 生成的稠密向量固定是 1024 维，原来写 1536 会插入失败
    # （报错：the length(20480) of float data should divide the dim(1536)）
    schema.add_field(
        field_name="vector",
        datatype=DataType.FLOAT_VECTOR,
        dim=1024
    )

    # 稀疏向量字段：bge-m3 的词权重字典，不用指定 dim
    schema.add_field(
        field_name="sparse_vector",
        datatype=DataType.SPARSE_FLOAT_VECTOR,
    )

    # 元数据：JSON 类型，可以存任意结构的字典
    schema.add_field(
        field_name="metadata",
        datatype=DataType.JSON
    )

    # 原文：VARCHAR 必须指定 max_length
    # 修改点 2：4096 跟插入脚本保持一致，原来 3000 偏小，长文本可能被截断
    schema.add_field(
        field_name="text",
        datatype=DataType.VARCHAR,
        max_length=4096
    )
    return schema

def build_index():
    # 索引参数：没有索引就无法加载集合，也就查询不了、Attu 里看不到数据
    index_params = MilvusClient.prepare_index_params()

    # 稠密向量用 HNSW 索引，COSINE 余弦相似度（文本向量一般用余弦）
    # 注意：后面检索时 search_params 的 metric_type 也必须写 "COSINE"，两边要一致
    index_params.add_index(
        field_name="vector",
        index_type="HNSW",
        metric_type="COSINE",
    )

    # 稀疏向量用倒排索引，度量固定用 IP（内积）
    index_params.add_index(
        field_name="sparse_vector",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="IP"
    )
    return index_params

def create_collection(client: MilvusClient, collection_name: str):
    # 建集合的同时把索引一起建好（原来那份插入脚本只传了 schema，所以没索引）
    client.create_collection(
        collection_name=collection_name,
        schema=build_schema(),
        index_params=build_index()
    )


client = get_client()
res = client.list_collections()
print("现有集合：", res)

create_collection(client=client, collection_name="demo_collection")
print("集合创建完成")

