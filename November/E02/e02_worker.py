import asyncio
from time import perf_counter


async def  run_worker(delay_ms:int,mode:str):
    await asyncio.sleep(delay_ms/1000)

    if mode == "error":
        raise RuntimeError("模拟执行失败")

    return "success"

#用于限制并发
async def limited_worker(semaphore, stats: dict, item_id: str,delay_ms: int, mode: str, timeout_ms: int,):
    async with semaphore:
        stats["active"] += 1
        stats["peak"] = max(stats["peak"], stats["active"])

        try:
            await asyncio.wait_for(
                run_worker(delay_ms, mode),
                timeout=timeout_ms / 1000,
            )
            return {
                "id": item_id,
                "status": "success",
                "error_code": None,
            }

        except TimeoutError:
            return {
                "id": item_id,
                "status": "timeout",
                "error_code": "worker_timeout",
            }

        except RuntimeError:
            return {
                "id": item_id,
                "status": "error",
                "error_code": "worker_failed",
            }

        finally:
            stats["active"] -= 1


#记录每个子任务的执行结果，统计成功、失败、超时的数量，并返回批次的整体状态。
def summarize_results(results:list):
    counts={"success":0,"error":0,"timeout":0}
    for result in results:
        counts[result["status"]] += 1
    if counts["success"] == len(results):
        batch_state = "success"
    elif counts["success"]==0:
        batch_state = "failed"
    else:
        batch_state = "partial"
    return {
        "status": batch_state,
        "counts": counts,
    }


async def execute_batch(request_id:str,items:list[dict],max_concurrency:int,timeout_ms:int):
    semaphore = asyncio.Semaphore(max_concurrency)
    stats = {"active":0,"peak":0}
    start = perf_counter()
 #列表推导式，与下列写法含义一致
    jobs =[
        asyncio.create_task(
            limited_worker(
                semaphore,
                stats,
                item["id"],
                item["delay_ms"],
                item["mode"],
                timeout_ms,
            )
        )
        for item in items
    ]

    try:
        results = await asyncio.gather(*jobs)
    finally:
        for job in jobs:
            if not job.done():
                job.cancel()
    #等待子任务的finally 执行完成，不让清理阶段的异常中断收尾
        await asyncio.gather(*jobs,return_exceptions = True)
    # 临时观察清理结果，后续移到测试中检查。
        print(f"清理后活跃度{stats['active']}")
        print("子任务已经解散",all(job.done()for job in jobs))
    summary = summarize_results(results)

    return{
        "request_id": request_id,
        "status": summary["status"],
        "items": results,
        "counts": summary["counts"],
        "metrics":{
            "latency_ms":int((perf_counter()-start)*1000),
            "peak_active": stats["peak"],
        },
    }
  
async def demo_variant():
    result = await execute_batch(
        request_id="variant-001",
    items=[
        {"id": "A", "delay_ms": 20, "mode": "ok"},
        {"id": "B", "delay_ms": 20, "mode": "error"},
        {"id": "C", "delay_ms": 10, "mode": "ok"},
    ],
    max_concurrency=2,
    timeout_ms=60,
)
    assert result["status"] == "partial"
    assert result["counts"] == {
        "success": 2,
        "error": 1,
        "timeout": 0,
    }
    assert result["items"] == [
    {"id": "A", "status": "success", "error_code": None},
    {"id": "B", "status": "error", "error_code": "worker_failed"},
    {"id": "C", "status": "success", "error_code": None},
]
    assert result["metrics"]["peak_active"] <=2
    


async def demo_cancel():
    batch = asyncio.create_task(
        execute_batch(
            request_id="cancel-demo",
            items=[
                {"id": "A", "delay_ms": 1000, "mode": "ok"},
                {"id": "B", "delay_ms": 1000, "mode": "ok"},
                {"id": "C", "delay_ms": 1000, "mode": "ok"},
            ],
            max_concurrency=2,
            timeout_ms=5000,
        )
    )

    # 将执行机会交给其他任务，稍后发出取消请求。
    await asyncio.sleep(0.05)

    batch.cancel()

    try:
        await batch
        print("意外：批次正常返回")
    except asyncio.CancelledError:
        print("调用方收到批次取消")

    print("批次已取消：", batch.cancelled())


async def main():
    items = [
        {"id": name, "delay_ms": 50, "mode": "ok"}
        for name in ["A", "B", "C", "D", "E"]
    ]

    for limit in [2,1]:
        result = await execute_batch(
            request_id =f"limit-{limit}",
            items = items,
            max_concurrency = limit,
            timeout_ms = 60,
        )
        print("并发上限",limit)
        print(result)

        assert result["counts"] == {
            "success": 5,
            "error": 0,
            "timeout": 0,
        }
        assert result["metrics"]["peak_active"] == limit

    await demo_variant()
    await demo_cancel()
if __name__ == "__main__":
    asyncio.run(main())        
