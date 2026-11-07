"""J01：把任务结果筛选需求变成一个自己实现的函数。"""


def select_results(results: list[dict], status: str) -> list[dict]:
    validate_results(results)
    if status not in ("success", "error", "timeout"):
        raise ValueError("Invalid status")
    selected = []
    for item in results:
        if item["status"] == status:
            selected.append(item)
    return selected


def make_report(results: list[dict], status: str) -> dict:
    result = select_results(results, status)
    return {
        "total": len(results),
        "matched": len(result),
        "items": result,
        "counts": count_status(results),
    }

def make_failure_report(results: list[dict]) -> dict:
    validate_results(results)
    selecte = []
    for item in results:
        if item["status"] in ("error", "timeout"):
            selecte.append(item)
    return {
        "total": len(results),
        "matched": len(selecte),
        "items": selecte,
        "counts": count_status(results),
    }

def validate_results(results: list[dict]) -> None:
    for item in results:
        if item["status"] not in ("success", "error", "timeout"):
            raise ValueError(
                f"任务 {item['id']} 的状态非法：{item['status']},",
            )

def count_status(results: list[dict]) -> dict:
    validate_results(results)
    counts = {
        "success": 0,
        "error": 0,
        "timeout": 0,
    }
    for item in results:
        if item["status"] in ("success", "error", "timeout"):
            counts[item["status"]] += 1
    return counts
    

if __name__ == "__main__":
    results = [
        {"id": "A", "status": "success", "error_code": None},
        {"id": "B", "status": "error", "error_code": "worker_failed"},
        {"id": "C", "status": "timeout", "error_code": "worker_timeout"},
        {"id": "D", "status": "success", "error_code": None},
        {"id": "E", "status": "error", "error_code": "worker_failed"},
    ]
    print(make_failure_report(results))

