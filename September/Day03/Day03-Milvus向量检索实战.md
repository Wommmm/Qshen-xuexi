# Day03 · Milvus 向量数据库实战

> 目标：用 Milvus + bge-m3 搭建一套可运行的向量检索系统
> 成果：完成「建集合 → 建索引 → 写入 → 检索 → 混合检索」完整链路

---

## 一、这一天的四个脚本

| 脚本 | 作用 | 执行顺序 |
|---|---|---|
| `mlivues_create.py` | 定义 Schema + 索引，**创建集合** | ① |
| `mlivues_create_index.py` | 给已存在的集合**单独补索引** | ②（可选） |
| `mlivues_create.data.py` | 加载 docx → 切分 → bge-m3 向量化 → **写入数据** | ③ |
| `mlivues_search.py` | **稠密检索 + 混合检索** | ④ |

**标准执行顺序**：

```bash
python mlivues_create.py        # 建集合（含索引）
python mlivues_create.data.py   # 插入 20 条数据
python mlivues_search.py        # 检索
```

> 如果集合已存在但没索引（Attu 显示"向量索引不存在"），单独跑一次 `mlivues_create_index.py`

---

## 二、数据是怎么组织的

### Collection 结构（相当于一张表）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | Int64（主键） | 每条数据的唯一标识 |
| `vector` | FloatVector(1024) | **稠密向量**，bge-m3 生成，1024 维 |
| `sparse_vector` | SparseFloatVector | **稀疏向量**，{词 id: 权重} 字典 |
| `text` | VarChar(4096) | 原文片段 |
| `metadata` | JSON | 文档元数据 |

### 数据流向

```
sample.docx（民法典）
   ↓ 加载
原始文本
   ↓ 切分（chunk_size=500, overlap=100）
20 个文本块
   ↓ bge-m3 编码
20 组「稠密向量 + 稀疏向量」
   ↓ 写入 Milvus
demo_collection（20 条实体）
```

---

## 三、核心概念

### 稠密向量 vs 稀疏向量

| | 稠密向量 | 稀疏向量 |
|---|---|---|
| 形态 | 1024 个小数，全都有值 | 词表 25 万维，只有几十个非零 |
| 本质 | 整段话的语义坐标 | 可学习的加权词袋 |
| 擅长 | 同义改写、跨说法召回 | 精确命中术语、专有名词 |
| 弱点 | 抓不住精确术语 | 不懂同义 |
| Milvus 字段 | `FLOAT_VECTOR`（要写 dim） | `SPARSE_FLOAT_VECTOR`（不写 dim） |
| 索引 | HNSW | SPARSE_INVERTED_INDEX |
| 度量 | COSINE / L2 | **IP（内积）** |

### 为什么必须混合

用户既会问「电池不耐用了怎么办」（要靠语义），也会问「HNSW 参数怎么调」（要靠关键词）。单一路必有盲区，所以**两路召回 + RRF 融合**。

### RRF 融合公式

```
score(d) = Σ  1 / (k + rank_i(d))      k 一般取 60
```

**只看排名，不看分数** —— 因为两路的相似度分数尺度完全不同（余弦 0~1，内积可能是 20+），无法直接相加。RRF 天然免归一化，且"两路都靠前"的文档自动胜出。

---

## 四、检索的三种写法

### 1. 稠密检索

```python
res = client.search(
    collection_name="demo_collection",
    data=[dense_vec],                    # 1024 维 list
    anns_field="vector",
    limit=5,
    search_params={"metric_type": "COSINE"},
    output_fields=["text"],
)
```

### 2. 稀疏检索

```python
res = client.search(
    collection_name="demo_collection",
    data=[sparse_vec],                   # {token_id: 权重}
    anns_field="sparse_vector",
    limit=5,
    search_params={"metric_type": "IP"},
    output_fields=["text"],
)
```

### 3. 混合检索（推荐）

```python
from pymilvus import AnnSearchRequest, RRFRanker

dense_request = AnnSearchRequest(
    data=[dense_vec], anns_field="vector",
    param={"metric_type": "COSINE"}, limit=50,
)
sparse_request = AnnSearchRequest(
    data=[sparse_vec], anns_field="sparse_vector",
    param={"metric_type": "IP"}, limit=50,
)

res = client.hybrid_search(
    collection_name="demo_collection",
    reqs=[dense_request, sparse_request],
    ranker=RRFRanker(k=60),              # 只接受 k 一个参数
    limit=3,
    output_fields=["text"],
)
```

> 两路各召回 50，最终只取 3 —— 给融合留空间。

---

## 五、实战结果

query：**「国家所有权」**

**稠密检索**（top_k=1）：
```python
{'id': 1, 'distance': 0.5689, 'entity': {'text': '...第五章　国家所有权和集体所有权、私人所有权...'}}
```
命中正确——文本块里确实包含"国家所有权"这几个字。0.5689 属于中等相关（命中的是目录页而非正文）。

**混合检索**（top_k=3）：
```python
{'id': 1, 'distance': 0.032787}
{'id': 0, 'distance': 0.016129}
{'id': 3, 'distance': 0.016129}
```

分数反推排名（k=60）：

| 文档 | 分数 | 反推 |
|---|---|---|
| id=1 | 0.032787 = 1/61 + 1/61 | **稠密第1 + 稀疏第1** |
| id=0 | 0.016129 = 1/62 | 某一路第2 |
| id=3 | 0.016129 = 1/62 | 某一路第2 |

**id=1 在两路都是第一名，分数正好是其他条目的两倍** —— 完美验证了 RRF 的融合逻辑：两路共同认可的排最前。

---

## 六、踩坑记录

| # | 报错 | 原因 | 解决 |
|---|---|---|---|
| 1 | `uri ... is illegal` | uri 没带协议 | 加 `http://` 或 `tcp://` |
| 2 | `length(20480) should divide dim(1536)` | 集合建成 1536 维，bge-m3 是 1024 | `dim=1024` |
| 3 | Attu 显示空 | 建集合时**没传 index_params** | 建集合时传索引，或单独 `create_index` |
| 4 | 查不到数据 | 集合没 load | `flush` + `load_collection` |
| 5 | `create duplicate collection with different parameters` | 同名集合参数不一致 | 先 `drop_collection` |
| 6 | 数据变成 80 条 | `insert` 对相同主键是追加 | 改用 `upsert` |
| 7 | `search_data is illegal` | 把 `encode()` 的整个字典传进去了 | 取 `["dense_vecs"][0]` |
| 8 | `unexpected keyword argument 'params'` | 参数名错了 | `params` → `param` |
| 9 | `fieldName(dense_vector) not found` | 字段名写错 | 稠密字段叫 `vector` |
| 10 | `RRFRanker() got unexpected argument` | 往 RRF 里塞了度量参数 | `RRFRanker(k=60)`，它只要 k |
| 11 | 稀疏检索报错 | 稀疏传了 COSINE | 稀疏**只能用 IP** |
| 12 | `hybrid_search() missing arguments` | 调用时参数个数对不上 | 按函数签名补齐 5 个参数 |

---

## 七、完整链路总结

```
建集合（带 index_params）
    ↓
插入数据（insert / upsert）
    ↓
flush（落盘）
    ↓
load_collection（加载到内存）← 没这步查不到数据
    ↓
search / hybrid_search
    ↓
结果拼成上下文 → 送给 LLM（RAG 最后一步）
```

---

## 八、后续计划

- [ ] 加 Reranker（bge-reranker-v2-m3）做两阶段精排
- [ ] 写评测脚本（hit@5、MRR），量化检索效果
- [ ] 接 LLM 完成 RAG 问答
- [ ] 用 FastAPI 封装成接口
