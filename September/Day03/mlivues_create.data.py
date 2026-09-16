from pymilvus import MilvusClient,DataType
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
def get_client():
    return MilvusClient(uri="tcp://127.0.0.1:19530")
def insert_data(client:MilvusClient,collection_name:str):
    """
    建构数据，插入collection中
    """
#1.加载一个文件，
    # 修复：load 加上()
    doc_list = UnstructuredWordDocumentLoader(r"D:\LANGCHANINDEMO\september\lianxineir\sample.docx",mode="single").load()
#2.切分文件
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=100,separators=["\n\n", "\n", "。", "！", "？", "……", "，", ""],)
    splitted_doc_list = text_splitter.split_documents(doc_list)
    splitted_doc_list = splitted_doc_list[0:20]
#查看当前文本列表当中最大的文本长度
    max_len = max([len(doc.page_content) for doc in splitted_doc_list ])
    print("当前最大长度",max_len)
#3.构建向量：稠密向量，稀疏向量
    from FlagEmbedding import BGEM3FlagModel
    # 修复：加上use_fp16=False适配CPU
    model = BGEM3FlagModel(r"D:\LANGCHANINDEMO\assets\models\bge-m3", use_fp16=False)
    all_vectors = model.encode([doc.page_content for doc in splitted_doc_list],return_dense=True,return_sparse=True)
#稠密向量
    dense_vectors = all_vectors["dense_vecs"]
#稀疏向量
    #修复拼写错误 vevtors → vectors
    sparse_vectors = all_vectors['lexical_weights']
#4.准备数据，组装成list[Dict]
    insert_data_list=[]
    #修复：增加idx生成主键id，dense_vec调用tolist()，修正循环变量
    for idx,(doc,dense_vec,sparse_vec)  in enumerate(zip(splitted_doc_list,dense_vectors,sparse_vectors)):
        insert_data_list.append({
            "id": idx, # Milvus主键必须存在
            "vector":dense_vec.tolist(), # numpy数组转list
            "sparse_vector":sparse_vec,
            "metadata":doc.metadata,
            "text":doc.page_content
        })
#5.调用client.insert()方法，插入数据（移出for循环，只执行一次批量插入）
    res = client.insert(
       collection_name = collection_name,
       data=insert_data_list
    )
    print(res)

if __name__ == "__main__":
    client = get_client()
    # 这里调用创建集合函数（你自己写好的build_schema/build_index）
    # create_coll(client)

    # 修复：bge-m3 的稠密向量是 1024 维，集合的 dim 必须一致（原来建成了 1536，所以插入报
    # "the length(20480) of float data should divide the dim(1536)"）
    DIM = 1024
    need_create = True
    if client.has_collection("demo_collection"):
        for f in client.describe_collection("demo_collection")["fields"]:
            if f["name"] == "vector" and f.get("params", {}).get("dim") == DIM:
                need_create = False
    if need_create:
        if client.has_collection("demo_collection"):
            client.drop_collection("demo_collection")
        schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=True)
        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=DIM)
        schema.add_field("sparse_vector", DataType.SPARSE_FLOAT_VECTOR)
        schema.add_field("text", DataType.VARCHAR, max_length=4096)
        client.create_collection("demo_collection", schema=schema,indexes=[{"field":"vector"}])
        print("已重建 demo_collection，dim =", DIM)

    insert_data(client, "demo_collection")
