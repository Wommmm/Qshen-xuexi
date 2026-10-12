from langchain_core.messages import SystemMessage
from datetime import datetime


#Middlewate,后面会传多个，所以我们在middleware中，不定义__call__方法
class BaseMiddleware:

    def before_agent(self,state) -> dict:
        pass

    def before_model(self,state) -> dict:
        pass



class DemoMiddleware(BaseMiddleware):
    def before_agent(self,state) -> dict:
        messages = state["messages"]
        system_message = SystemMessage(
            content = "当前时间为" + datetime.now().strftime("%Y-%m-%d %H:%M:%S")+","+"当前是周"+(datetime.now().weekday())
        )
        return {"messages":[system_message]}
