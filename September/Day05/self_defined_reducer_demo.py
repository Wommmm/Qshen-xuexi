from langgraph.graph import StateGraph
from langchain_core.messages import ToolMessage,HumanMessage,AIMessage,BaseMessage,AnyMessage
from typing import Annotated, TypedDict,List
from langgraph.constants import START
from mcp import Tool

#自定义一个reducer：将全局messages状态和节点输出的messages状态，做一个合并
def my_add_messages_reducer (messages_list_left:List[AnyMessage],messages_list_right:List[AnyMessage])->List[AnyMessage]:
     new_messages = messages_list_left + messages_list_right
     print("正在调用自定义reducer")
     print("messages_list_left",messages_list_left)
     print("messages_list_right",messages_list_right)

     return new_messages


class MYagentState(TypedDict):
     messages:Annotated[List[AnyMessage],my_add_messages_reducer]

def mock_invoke_llm(messages_list:List[AnyMessage]):
     
     return AIMessage(content="llm节点输出",tool_call_id="asd")

def llm_node(state: MYagentState):
     messages_list = state["messages"]

     #拿到所有的messages_list ，然后拿到llm.invoke(messages_list)
     ai_message = mock_invoke_llm(messages_list)
     return {"messages":[ai_message]}


def tool_node(state: MYagentState):
     #去最后一条ai_message :通常这个ai_message会携带tool_call

     last_ai_message = state["messages"][-1]
     
     tool_message = mock_invoke_llm(last_ai_message)

     return {"messages":[tool_message]}


builder = StateGraph(MYagentState)
builder.add_node(llm_node)
builder.add_node(tool_node)
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", "tool_node")
graph = builder.compile()
res =  graph.invoke({"messages":[HumanMessage(content="你好")]})
print(res)