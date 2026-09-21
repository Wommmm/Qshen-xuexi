from operator import add 
import operator
from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    """
    状态类型定义
    """
    aggregate: Annotated[list, operator.add]

def a(state: State,config):
    print(f'Adding "A" to {state["aggregate"]}')
    return {"aggregate": ["A"]}

def b(state: State,config):
    print(f'Adding "B" to {state["aggregate"]}')
    return {"aggregate": ["B"]}

def b_2(state: State,config):
    print(f'Adding "B_2" to {state["aggregate"]}')
    return {"aggregate": ["B_2"]}

def c(state: State,config):
    print(f'Adding "C" to {state["aggregate"]}')
    return {"aggregate": ["C"]}

def d(state: State,config):
    print(f'Adding "D" to {state["aggregate"]}')
    return {"aggregate": ["D"]}

builder = StateGraph(State)

builder.add_node("a", a)
builder.add_node("b", b)
builder.add_node("b_2", b_2)
builder.add_node("c", c)
builder.add_node("d", d)

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b_2")
builder.add_edge("b_2", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)

graph = builder.compile()
# 1、查看当前图的channels
print('当前图的channels为',graph.channels,end="\n\n")
# 2、查看当前图的节点
print('当前图的节点为',graph.nodes,end="\n\n")

# 3、查看a节点的trigger（当前节点的订阅）和writers
print('当前图的节点a的triggers为',graph.nodes['a'].triggers,end="\n\n")
print('当前图的节点a的writers为',graph.nodes['a'].writers,end="\n\n")

# 4、查看d节点的trigger和writers
print('当前图的节点d的triggers为',graph.nodes['d'].triggers,end="\n\n")
print('当前图的节点d的writers为',graph.nodes['d'].writers,end="\n\n")
# 5、执行图，查看执行结果
output_state = graph.invoke({"aggregate": []}) 
print('执行图后的状态为',output_state,end="\n\n")
