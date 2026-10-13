import asyncio
import time

async def call_model(name:str,delay:float):
    await asyncio.sleep(delay)
    return f"{name} completed"

async def main():
    #高精度测量时间间隔
    start = time.perf_counter()
    #并发运行多个 awaitable
#gather() 会把这三个协程安排到事件循环中并发执行，并等待它们全部成功完成后返回结果。
    results = await asyncio.gather(
        call_model("gpt",3),
        call_model("claude",2),
        call_model("deepseek",1),
    )
    print (results)
    print(f"总耗时：{time.perf_counter()-start:.2f}s")

asyncio.run(main())
###为什么是三秒，并发与并行不同，
#并发：多个任务在同一段时间内交替推进
#并行：多个任务同时进行，但多个任务之间没有依赖关系
async def task(name, delay):
    print(f"{name} start")
    await asyncio.sleep(delay)
    print(f"{name} end")


async def main2():
    await task("A", 2)
    await task("B", 1)

asyncio.run(main2())