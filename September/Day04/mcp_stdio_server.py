from mcp.server import FastMCP

#定义一个mcp的服务端
mcp = FastMCP()

@mcp.tool()
def add(a: int, b: int) -> int:
    """计算两个数的和"""
    return a + b

@mcp.tool()
def get_weather(city: str, date: str) -> str:
    """获取城市的天气"""
    return f"城市{city}在{date}的天气是晴朗的"

@mcp.resource("greeting://default")
def get_greeting() -> str:
    return "Hello from static resource!"

@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    styles = {
        "friendly": "写一句友善的问候",
        "formal": "写一句正式的问候",
        "casual": "写一句轻松的问候",
    }
    return f"为{name}{styles.get(style, styles['friendly'])}"

if __name__ == "__main__":
    mcp.run(transport="stdio")