import time
from typing import TypedDict, Any, List
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime

class MockLLM:
    def invoke(self, prompt: str):
        return f"AI Generated: Answer for '{prompt}'"

class MockDatabase:
    def get_user_info(self, user_id: str):
        return {"id": user_id, "role": "vip" if "vip" in user_id else "standard"}

class CustomerSupportState(TypedDict):
    query: str          # 用户问题
    response: str       # 客服回复
    log: List[str]      # 处理日志

def node_customer_service(
        state: CustomerSupportState,
        config: RunnableConfig,
        runtime: Runtime) -> dict:
    """
    客服节点：展示如何从 config 中获取注入的依赖 (LLM, DB) 并使用 runtime 推送进度。
    """
    print("客服节点开始执行")
    print("传入的状态为",state)
    print("传入的配置为",config)
    print("当前调用该用户的ID为",config["configurable"]["user_id"])
    print("传入的运行时为",runtime)

builder = StateGraph(CustomerSupportState)
builder.add_node(node_customer_service)
builder.add_edge(START,"node_customer_service")

graph = builder.compile()

#调用invoke时，可以传递相关的配置信息和整个图执行过程中上下文/运行时数据
cofig = {"user_id":"vip_123"}

context = {"llm":MockLLM(), "db":MockDatabase()}

res = graph.invoke({"query":"你好"},config=cofig,context=context)
print(res)
                     