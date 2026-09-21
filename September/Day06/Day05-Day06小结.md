# LangGraph · Day05 + Day06 小结

> 2026-09-22 · 目录：`D:\LANGCHANINDEMO\september\Day05` `Day06`
> 用法：手机上看这张表 → 想不起来的点，回去打开对应文件跑一遍

---

## 一、Day05 · 状态与图结构

| 文件 | 学什么 | 一句话记住 |
|---|---|---|
| `langgraph_get_started_demo.py` | State + 节点 + 边 + **并行扇出** | 两路检索同时跑，最后汇总 |
| `input_output_demo.py` | `input_schema` / `output_schema` | **过滤进出图的字段**：外面只能传 `query`、只能拿到 `answer` |
| `private_state_demo.py` | 私有状态 | 节点返回 State 里**没定义**的 key（如 `a_new_key`）也能往下传 |
| `reducer_demo.py` | `Annotated[List, add]` | 并行节点写同一个 key 时，靠 reducer 合并而不是互相覆盖 |
| `self_defined_reducer_demo.py` | 自定义 reducer | 自己写合并逻辑（messages 列表累加） |
| `state_history_demo.py` | `get_state` / `get_state_history` | 看每一步的历史快照（**必须配 checkpointer**） |
| `state_resume.py` | `SqliteSaver` + `invoke(None)` | 崩了能从断点续跑 |
| `test_demo.py` | `graph.channels` / `nodes` / `triggers` | 看图的内部结构（谁订阅了谁） |

## 二、Day06 · 节点的输入输出与工程能力

| 文件 | 学什么 | 一句话记住 |
|---|---|---|
| `01_node_input.py` | 节点第三个参数 `runtime`，`invoke(config=, context=)` | **依赖注入**：LLM 和 DB 从外面传进来，节点不自己 new |
| `02_node_output.py` | 节点返回值（**反例演示**） | 注释里写的是错误写法：直接 `return state`；正确是**只返回增量** |
| `03_noed_cache.py` | `CachePolicy(ttl=3)` + `InMemoryCache` | 节点级缓存，ttl 秒内重复调用直接返回 |
| `04_noed_retry.py` | `RetryPolicy()` | 失败自动重试，间隔是指数退避（1s/2s/4s…） |
| `05_node_stream_output.py` | `stream_mode` | `values` / `updates` / `messages` 三种，见下表 |

---

## 三、三个必须记住的核心概念

**1. State 的字段 = 通道**
外面传什么 key，State 一开始就有什么；节点只能读**存在的** key，读没有的就 `KeyError`。

**2. Reducer 解决"并行冲突"**
两个节点同时写同一个 key，默认是**后者覆盖前者**；想保留全部就加 reducer（`add` 或自定义函数）。

**3. 流式是两件事叠加**
> `stream_mode` 决定**你怎么接收**；LLM 的调用方式决定**有没有东西可以流**。

| stream_mode | 吐什么 | 什么时候吐 |
|---|---|---|
| `values` | 完整 State（dict） | 每个节点执行完 → **N 个节点输出 N+1 次** |
| `updates` | 本节点的增量 | 每个节点执行完 |
| `messages` | `(token片段, metadata)` | LLM 每产一个 token |

---

## 四、踩坑表（今晚真实踩过的）

| 坑 | 现象 | 怎么避 |
|---|---|---|
| 传进去的 key 和节点读的 key 不一致 | **`KeyError: 'query'`** | `{"llm_message": ...}` 改成 `{"query": ...}` |
| 节点里用 `llm.invoke()` 想看流式 | 内容一次全出来，不逐字 | 节点里换 `llm.stream()` |
| 用 `values` 期待看到逐字输出 | 只看到状态快照 | 想看 token 就用 `messages` |
| 节点忘了 `return` | 字段写不进 State，白跑 | 每个节点必须有返回值 |
| 写成 `State["query"]`（大写） | 拿到的是类不是实例 | 应该是 `state["query"]` |
| `metadata` 当成内容用 | 取不到文本 | 内容在 `chunk.content`，metadata 只是来源信息 |

**另外**：`TypedDict` **运行时不校验类型** —— `llm_message: list` 里存字符串也不报错（跟 Pydantic 不一样）。标注是写给自己看的，别写错。

---

## 五、三句话自检（能讲出来就算真懂）

1. State 里一个字段就是一条通道，节点只能读已经存在的 key。
2. Reducer 是"并行节点写同一个 key 时怎么合并"的规则。
3. `stream_mode` 决定接收方式，LLM 的调用方式决定有没有 token 可流。

---

## 六、欠账（明天补）

- ⬜ **条件边**（`add_conditional_edges` + 路由函数）—— 课件「条件边」一节，作业写了没跑
- ⬜ **可控循环**（route 返回 `END` 或节点名 + `recursion_limit`）—— 课件「可控循环」一节
- ⬜ 真流式：`05_node_stream_output.py` 里把 `res = "调用结果"` 换成 `llm.stream()`
