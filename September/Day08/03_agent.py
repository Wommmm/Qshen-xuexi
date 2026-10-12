
"""
写一个create_agent函数：接受tools,middlleware_list,system_prompt等参数
使用langgraph去构建graph

"""
import os 
from tool_node import ToolNode
from langgraph.graph import StateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver
from operator import add
from langchain_openai import ChatOpenAI
from typing import Annotated, Any, List ,Dict,  TypedDict
from langchain_core.messages import SystemMessage , HumanMessage,HumanMessage,AIMessage,AnyMessage
def create_agent(
        model: ChatOpenAI,
        tools: list,
        system_prompt: str,
        middleware_list: list,
        checkpointer: BaseCheckpointSaver
): 
    class MyagentState(TypedDict):
        messages: Annotated[list[AnyMessage],add ]

    def model_node(state:MyagentState):
        messages = state["messages"]
        ai_message = model.invoke(messages)
        return {"messages":[ai_message]}

    tool_node = ToolNode(tools)

    def _merge_middleware_update(update:dict, mw_upadte_state:dict):
        if mw_upadte_state is None:
            return 
        for k,v in mw_upadte_state.items():
            if k not in update:
                update[k] = v
            else:
                update[k] += v

    
    if middleware_list:
        def middleware_node(state:MyagentState):
            update:dict={}
            for mw in middleware_list:

             mw_upadte_state = mw.before_model(state)

            return  update  

    def  before_model_node(state:MyagentState):
        update:dict={}
        for mw in middleware_list:
            mw_upadte_state = mw.before_model(state)
            _merge_middleware_update(update,mw_upadte_state)
        return update
    def conditional_edge_func(state:MyagentState):
        messages = state["messages"]
        if messages and type(messages[-1]) == AIMessage and messages[-1].tool_calls:
            return "tool_node"
        else:
            return "__end__"
#添加节点和边
    builder = StateGraph(state_schema =MyagentState)
    builder.add_node(model_node)
    builder.add_node(tool_node)
    if middleware_list:
        builder.add_node(before_agent_node)
        builder.add_node(before_model_node)
        builder.add_edge("__start__","before_agent")
        builder.add_edge("before_agent","before_model_node")
        builder.add_edge("before_model_node","moedel_node")
        builder.add_conditional_edge("model_node",conditional_edge_func)
        builder.add_edge("tool_node","before_model_node")
    else:
        builder.add_edge("__start__","model_node")
        builder.add_conditional_edge("model_node",conditional_edge_func)
        builder.add_edge("tool_node","model_node")

    graph = builder.compile(
        checkpointer=checkpointer
    )    
    return graph

   
         
