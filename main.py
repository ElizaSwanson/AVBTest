import asyncio

import aiohttp
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import string
import random

from pydantic import BaseModel
from starlette import status

app = FastAPI()

#just keeping urls in memory instead of DB
url_storage = {}
url_storage["test123"] = "https://google.com"

class URLRequest(BaseModel):
    url: str


def generate_short_id(length=10):
    while True:
        short_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if short_id not in url_storage:
            return short_id


@app.get("/")
async def root():
    return {"message": "Server is working!"}


@app.get("/url-headers/{short_id}")
async def get_url_headers(short_id: str):
    """async request and getting header from original website"""

    original_url = url_storage.get(short_id)
    if not original_url:
        raise HTTPException(status_code=404, detail="URL not found")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(original_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                return {
                    "original_url": original_url,
                    "short_id": short_id,
                    "status_code": response.status,
                    "headers": dict(response.headers)
                }

    except Exception as e:
        return {"status": "error", "message": f"Request failed: {str(e)}"}


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_short_url(data: URLRequest):
    """making a short version of url"""
    short_id = generate_short_id()
    url_storage[short_id] = data.url
    return {"short_id": short_id, "short_url": f"http://127.0.0.1:8000/{short_id}"}


@app.get("/{short_id}")
async def redirect(short_id: str):
    original_url = url_storage.get(short_id)
    if not original_url:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(url=original_url, status_code=307)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)