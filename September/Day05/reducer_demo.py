from re import L
from typing import TypedDict,List,Annotated
from langgraph.graph import StateGraph
from langgraph.constants import START,END
from operator import add
#1.定义状态
class MYagentState(TypedDict):
    """
    运用python原生的typing 模块定义一个字典，

    """
    query: str
    rag_search:str
    web_search: str
    llm_answer: str
    #operator.add:接受两个值，放回一个结果 operator.add（2，3）=5合并两个列表
    #add函数在langgraph中称为为Reducer函数
    test_key:Annotated[List[str],add]


#2定义节点
def rag_node(state: MYagentState):
    #1.从state中获取query
    query = state["query"]

    #2模拟rag检索
    rag_search = f"根据用户的问题{query},从知识库中检索相关内容"
    #3.将rag_search写入到状态当中
    return {"rag_search": rag_search,"test_key":["test_key_rag_value"]}

def web_search_node(state: MYagentState):
    #1.从state中获取query
    query = state["query"]
    #2.模拟web检索
    web_search = f"根据用户问题{query},从互联网上检索相关内容"
    #3.将web_search写入到状态当中
    return {"web_search": web_search,"test_key":["test_key_web_value"]}

def llm_mode(state: MYagentState):
    #1，从state中读取rag_search和web_search
    rag_search = state["rag_search"]
    web_search = state["web_search"]

    #2.模拟llm调用基于两路检索，生成最终答案

    llm_answer = f"根据用户问题,结合{rag_search}和{web_search}，生成最终答案"

    return {"llm_answer": llm_answer}

#3构建builder
bulider = StateGraph(state_schema=MYagentState)

#3.1添加节点
bulider.add_node(rag_node)#将add_dd_node底层会将节点名称设置为函数名

bulider.add_node(web_search_node)

bulider.add_node(llm_mode)

#3.2添加边
bulider.add_edge(START,"rag_node")

bulider.add_edge(START,'web_search_node')

bulider.add_edge("rag_node","llm_mode")

bulider.add_edge('web_search_node',"llm_mode")

#3.3添加结束节点
bulider.add_edge("llm_mode",END)

#4.构建图
graph = bulider.compile()

#5.执行图,因为graph的class实现了langgchain当中的Runnable接口
res = graph.invoke({"query": "如何使用langgraph"}) 

print(res)


