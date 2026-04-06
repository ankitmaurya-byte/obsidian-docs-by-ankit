```python

from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/async")
async def async_route():
    await asyncio.sleep(2)
    return {"message": "This is an async route"}
```

# pydantic
## data validation


# uvicorn 
## **ASGI server** — it runs your FastAPI app and handles HTTP connections

# supabase 
## Every query chain ends with .execute() — this actually sends the request to Supabase.

| `Pillow` | Image library (used for mock image generation) |
| -------- | ---------------------------------------------- |
