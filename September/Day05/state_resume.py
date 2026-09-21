from typing import Annotated, TypedDict,List
from langgraph.graph import StateGraph
from langgraph.constants import START
from langgraph.checkpoint.sqlite  import  SqliteSaver
import sqlite3
class ResumeDemoState(TypedDict):
    key_1:str
    key_2:str
    key_3:str

def node_1(state:ResumeDemoState):

    return {"key_1": "value_1"}

def node_2(state:ResumeDemoState):
    raise Exception("error")
    # print("2被调用了")
    return {"key_2": "value_2"}

def node_3(state:ResumeDemoState):
    print("3被调了")
    return {"key_3": "value_3"}

builder = StateGraph(ResumeDemoState)

builder.add_node(node_1)
builder.add_node(node_2)
builder.add_node(node_3)

builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")
builder.add_edge("node_2","node_3")

#构建一基于数据库的checkpointer
checkpointer = SqliteSaver(conn =sqlite3.connect("./resume_demo.db",check_same_thread=False))
graph = builder.compile(checkpointer=checkpointer)

res = graph.invoke({},config={"configurable":{"thread_id":"1"}})
print(res)

#从状态当中恢复执行
#传入None，表示从状态中恢复继续往下执行，如果传入字典dict，则表示从字典中恢复
res = graph.invoke(None,config={"configurable":{"thread_id":"1"}})