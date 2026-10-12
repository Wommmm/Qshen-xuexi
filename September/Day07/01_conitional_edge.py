from typing import TypedDict,Annotated
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy


class MyState(TypedDict):
   query:str
   number: int 
   node : str
   rag_message:str


def node_a(state:MyState):   
   
   number = state['number']

   print("正在执行node_a")

   return {"node":"node_b"}

def node_b(state:MyState):
   number = state['number']


   print("正在执行node_b")

   return {"node":"node_b", "number":number+2}

def conntionnal_function(state:MyState):
   """
   条件边函数，结合当前状态，判断下一节点
   """
   number = state['number']

   if number % 2 == 0:
        return "node_b"
   else:
        return "__end__"


builder = StateGraph(state_schema=MyState)

builder.add_node(node_a)
builder.add_node(node_b)
builder.add_edge("__start__", "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "__end__")
#引入条件边
builder.add_conditional_edges(
   #头执行哪一个节点
   source = "node_a",
   #可以传函数
   path=conntionnal_function
)

graph = builder.compile()

res = graph.invoke({"number":2})
print(res)
   