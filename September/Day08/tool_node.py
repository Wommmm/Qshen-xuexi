from typing import Sequence,Any
from unittest.mock import Base
from langchain.tools.base import BaseTool
from concurrent.futures import ThreadPoolExecutor
from langchain.messages import ToolMessage

class ToolNode :
   def __init__(self, tools:Sequence[BaseTool] |  None = None,max_workers=3):
      self.tools = tools
      self.max_workers = max_workers
      self.name_to_tool = {tool.name: tool for tool in self.tools}

   def __call__(self,state,retime) -> Any:
      message_list = state["messages"]  
      last_message = message_list[-1] #最后一个message 就是ai输出的message tool_calls
      tool_calls = last_message.tool_calls
      #将tool_calls提交到线程池执行
      with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
         #通过executor.map()方法将tool_calls提交到线程池执行
          #第一个参数，传递的线程需要执行的函数，
          #第二个参数，以list形式传递函数执行的参数
          result_generator = executor.map(lambda tool_call:self.execute_single_tool(tool_call), tool_calls)

          result:list[ToolMessage] = list(result_generator)

        #tool 节点对messages状态做增量更新
      return {"messages":result}
         
   def execute_single_tool(self,tool_call:dict) -> ToolMessage:
      """
      执行单个tool_call
      """        
      tool_name:str = tool_call["name"]
      tool_args:dict = tool_call["args"]
      tool_call_id:str = tool_call["id"]
      tool:BaseTool = self.name_to_tool[tool_name]
 
      try:
           res = tool.invoke(tool_args)
           return ToolMessage(
           content=res,
         tool_call_id=tool_call_id
      )
      except Exception as e:
          #写一个handler函数处理特殊情况，对不同情况封装痌conntent
          return ToolMessage(
           content=f"调用{tool_name}时发生异常：{e}",
           tool_call_id=tool_call_id
      )
       

