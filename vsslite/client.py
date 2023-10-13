import aiofiles
import aiohttp
from aiohttp.client_exceptions import ClientResponseError
import asyncio
import csv
import json
from logging import getLogger, NullHandler
import traceback
from typing import List

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class VSSLiteClient:
    def __init__(self, base_url: str="http://127.0.0.1:8000", timeout=10):
        self.base_url = base_url
        self.timeout = timeout
    
    def sync(self, future):
        return asyncio.get_event_loop().run_until_complete(future)
    
    async def aadd(self, body: str, data: dict=None, namespace: str="default") -> int:
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.post(
                    self.base_url + f"/knowledge/{namespace}",
                    json={"body": body, "data": data},
                    timeout=self.timeout
                ) as resp:
                    return (await resp.json())["id"]

        except Exception as ex:
            logger.error(f"Error at VSSEngine.add: {str(ex)}\n{traceback.format_exc()}")
            raise ex
    
    def add(self, body: str, data: dict=None, namespace: str="default") -> int:
        return self.sync(self.aadd(body, data, namespace))
    
    async def aupdate(self, id: int, body: str, data: dict=None) -> int:
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.patch(
                    self.base_url + f"/knowledge/{id}",
                    json={"body": body, "data": data},
                    timeout=self.timeout
                ) as resp:
                    return (await resp.json())["id"]
        
        except Exception as ex:
            logger.error(f"Error at VSSEngine.update: {str(ex)}\n{traceback.format_exc()}")
            raise ex

    def update(self, id: int, body: str, data: dict=None) -> int:
        return self.sync(self.aupdate(id, body, data))

    async def adelete(self, id: int):
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.delete(
                    self.base_url + f"/knowledge/{id}",
                    timeout=self.timeout
                ):
                    pass

        except Exception as ex:
            logger.error(f"Error at VSSEngine.delete: {str(ex)}\n{traceback.format_exc()}")
            raise ex
    
    def delete(self, id: int):
        self.sync(self.adelete(id))

    async def adelete_all(self):
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.delete(
                    self.base_url + f"/knowledge/all",
                    timeout=self.timeout
                ):
                    pass

        except Exception as ex:
            logger.error(f"Error at VSSEngine.delete_all: {str(ex)}\n{traceback.format_exc()}")
            raise ex
    
    def delete_all(self):
        self.sync(self.adelete_all())

    async def aget(self, id: int) -> dict:
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.get(
                    self.base_url + f"/knowledge/{id}",
                    timeout=self.timeout
                ) as resp:
                    return await resp.json()

        except ClientResponseError as crerr:
            if crerr.status == 404:
                return None
            logger.error(f"Error at VSSEngine.get: {str(crerr)}\n{traceback.format_exc()}")

        except Exception as ex:
            logger.error(f"Error at VSSEngine.get: {str(ex)}\n{traceback.format_exc()}")
            raise ex

    def get(self, id: int) -> dict:
        return self.sync(self.aget(id))

    async def asearch(self, query: str, count: int=1, namespace: str="default") -> List[dict]:
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.get(
                    self.base_url + f"/knowledge/{namespace}/search",
                    params={"q": query, "count": count},
                    timeout=self.timeout
                ) as resp:
                    return (await resp.json())["results"]

        except Exception as ex:
            logger.error(f"Error at VSSEngine.search: {str(ex)}\n{traceback.format_exc()}")
            raise ex
    
    def search(self, query: str, count: int=1, namespace: str="default") -> List[dict]:
        return self.sync(self.asearch(query, count, namespace))

    async def aload_records_as_json(self, path) -> List[dict]:
        async with aiofiles.open(path, mode="r", newline="") as file:
            content = await file.read()
            try:
                return json.loads(content)["records"]
            except Exception as ex:
                csv_lines = content.split("\n")
                reader = csv.DictReader(csv_lines)
                return [dict(r) for r in reader]

    async def aimport_file(self, path: str, body_key: str="body", namespace: str="default"):
        records = await self.aload_records_as_json(path)

        ret = {"ids": [], "errors": []}
        for r in records:
            try:
                if "id" in r:
                    ret["ids"].append(await self.aupdate(r["id"], r[body_key], r))
                else:
                    ret["ids"].append(await self.aadd(r[body_key], r, namespace))
            except Exception as ex:
                ret["errors"].append({"message": str(ex), "record": r})

        return ret

    def import_file(self, path: str, body_key: str="body", namespace: str="default"):
        return self.sync(self.aimport_file(path, body_key, namespace))
