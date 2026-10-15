import asyncio

def read_query(data):
    query = data.get("query")
    if not isinstance(query, str):
        raise ValueError("query必须是字符串")
    query = query.strip()
    if not query:
        raise ValueError("query为空")
    return query

async def fetch_documents(query:str):
    await asyncio.sleep(0.2)
    if query == "无资料":
     print("query为空")
     return []
    if query == "模拟故障":
       raise RuntimeError("检索服务不可用")
    return [{"content": "RS-12使用AA电池", "source": "local"}]

def prepare_documents(documents,top_k,source=None):   
   result=[]
   for doc in documents:
      if doc["content"].strip():
         if source is None or doc["source"] == source:
            result.append(doc)

   return result[:top_k]


async def handle_request(data,top_k=2,source=None):
   try:  
     query = read_query(data)   
     documents = await fetch_documents(query)
     documents = prepare_documents(documents,top_k,source)
     status = "ok"
     if not documents:
        status = "empty"
     return{
        "status": status,
        "documents": documents,
        "count": len(documents),
     }
   except ValueError:
      return {"status": "error", "error_code": "invalid_query", "documents": [], "count": 0}
   except RuntimeError:
      return  {"status": "error", "error_code": "retrieval_failed", "documents": [], "count": 0}
      
async def main():
   result= await handle_request({"query": "电池型号是什么？"},source="web")

   print(result)

if __name__ == "__main__":
   asyncio.run(main())

    



