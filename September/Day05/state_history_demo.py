from operator import add 
import operator
from typing import Annotated, Any
from emoji import config
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.memory  import  InMemorySaver

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

graph = builder.compile(checkpointer=InMemorySaver())

res = graph.invoke({},config={"configurable":{"thread_id":"1"}})

#1获取当前状态
state = graph.aget_state(config={"configurable":{"thread_id":"1"}})
print(state)

#2.获取到历史的所有状态
history_states = graph.get_state_history(config={"configurable":{"thread_id":"1"}})
for state in history_states:
    print(state)
    print("="*50)