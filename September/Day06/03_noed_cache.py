#节点缓存
from typing import TypedDict

class MyState(TypedDict):

    user_id:str
    order_id:str


def mock_get_order_id(user_id:str):
       import time
       time.sleep(1)

       return f"order_id_123_{user_id}"
def get_order_id(state:MyState):
      print("调用get_order_id")
      user_id = state['user_id']
      order_id = mock_get_order_id(user_id=user_id)

      return {"order_id": order_id}

from langgraph.graph import StateGraph

builder = StateGraph(state_schema=MyState)
#在需要调用缓存的节点，传入cache_policy
#Cachpoliy有两个属性，key_func 和 ttl
from langgraph.types import CachePolicy
builder.add_node(get_order_id,cache_policy=CachePolicy(ttl=3))
#"__start__" 其实就是langgraph.constants.START
builder.add_edge("__start__", "get_order_id")
#引入一个cacher,用来保存缓存数据
from langgraph.cache.memory import InMemoryCache
#在compile时，传入cacher
graph = builder.compile(cache = InMemoryCache())#传入cache，保证了graph用户拥有缓存能力

print("第一次调用")
res = graph.invoke({"user_id":"123"})
print("="*50)

print("第二次调用")
res = graph.invoke({"user_id":"123"})
print("="*50)

print("第三次调用")
res = graph.invoke({"user_id":"123"})
print("="*50)

print(res)