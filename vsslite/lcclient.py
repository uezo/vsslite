import asyncio
import base64
import csv
from dataclasses import dataclass
import json
from logging import getLogger, NullHandler
import os
import traceback
from typing import List

import aiofiles
import aiohttp
from aiohttp.client_exceptions import ClientResponseError

logger = getLogger(__name__)
logger.addHandler(NullHandler())


@dataclass
class Document:
    page_content: str
    metadata: dict


class LangChainVSSLiteClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout=120):
        self.base_url = base_url
        self.timeout = timeout

    def sync(self, future):
        return asyncio.get_event_loop().run_until_complete(future)

    async def asearch(self, query: str, count: int = 4, namespace: str = "default", score_threshold: float = 0.0) -> List[dict]:
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.get(
                    self.base_url + f"/search/{namespace}",
                    params={"q": query, "count": count, "score_threshold": score_threshold},
                    timeout=self.timeout
                ) as resp:
                    return (await resp.json())["results"]

        except Exception as ex:
            logger.error(f"Error at VSSClient.search: {str(ex)}\n{traceback.format_exc()}")
            raise ex

    def search(self, query: str, count: int = 4, namespace: str = "default") -> List[dict]:
        return self.sync(self.asearch(query, count, namespace))

    async def aget(self, id: str, namespace: str = "default") -> dict:
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.get(
                    self.base_url + f"/document/{namespace}/{id}",
                    timeout=self.timeout
                ) as resp:
                    return await resp.json()

        except ClientResponseError as crerr:
            if crerr.status == 404:
                return None
            logger.error(f"Error at VSSClient.get: {str(crerr)}\n{traceback.format_exc()}")

        except Exception as ex:
            logger.error(f"Error at VSSClient.get: {str(ex)}\n{traceback.format_exc()}")
            raise ex

    def get(self, id: str, namespace: str = "default") -> dict:
        return self.sync(self.aget(id, namespace))

    async def aget_all(self, namespace: str = "default") -> List[dict]:
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.get(
                    self.base_url + f"/document/{namespace}/all",
                    timeout=self.timeout
                ) as resp:
                    return await resp.json()

        except Exception as ex:
            logger.error(f"Error at VSSClient.get: {str(ex)}\n{traceback.format_exc()}")
            raise ex

    def get_all(self, namespace: str = "default") -> List[dict]:
        return self.sync(self.aget_all(namespace))

    async def aadd(self, documents: List[Document], namespace: str = "default") -> List[str]:
        try:
            if isinstance(documents, str):
                _documents = [Document(page_content=documents, metadata={"source": "inline"})]
            else:
                _documents = documents

            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.post(
                    self.base_url + f"/document/{namespace}",
                    json={"documents": [
                        {"page_content": d.page_content, "metadata": d.metadata}
                        for d in _documents]
                    },
                    timeout=self.timeout
                ) as resp:
                    ids = (await resp.json())["ids"]
                    if isinstance(documents, str):
                        return ids[0]
                    else:
                        return ids

        except Exception as ex:
            logger.error(f"Error at VSSEngine.add: {str(ex)}\n{traceback.format_exc()}")
            raise ex

    def add(self, documents: List[Document], namespace: str = "default") -> List[str]:
        return self.sync(self.aadd(documents, namespace))

    async def aupdate(self, ids: List[str], documents: List[Document], namespace: str = "default"):
        try:
            if isinstance(ids, str):
                _ids = [ids]
            else:
                _ids = ids

            if isinstance(documents, str):
                _documents = [Document(page_content=documents, metadata={"source": "inline"})]
            else:
                _documents = documents

            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.patch(
                    self.base_url + f"/document/{namespace}",
                    json={
                        "ids": _ids,
                        "documents": [
                            {"page_content": d.page_content, "metadata": d.metadata}
                        for d in _documents]
                    },
                    timeout=self.timeout
                ):
                    pass

        except Exception as ex:
            logger.error(f"Error at VSSEngine.update: {str(ex)}\n{traceback.format_exc()}")
            raise ex

    def update(self, ids: List[str], documents: List[Document], namespace: str = "default"):
        self.sync(self.aupdate(ids, documents, namespace))

    async def aupload(self, path: str, loader_params: dict = None, namespace: str = "default") -> List[str]:
        try:
            async with aiofiles.open(path, "rb") as file:
                binary_data = await file.read()

            b64content = base64.b64encode(binary_data).decode("utf-8")
            filename = os.path.basename(path)
            document_type = os.path.splitext(filename)[1]

            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.post(
                    self.base_url + f"/document/{namespace}/upload",
                    json={
                        "b64content": b64content,
                        "filename": filename,
                        "document_type": document_type,
                        "loader_params": loader_params
                    },
                    timeout=self.timeout
                ) as resp:
                    return (await resp.json())["ids"]

        except Exception as ex:
            logger.error(f"Error at VSSClient.aupload: {str(ex)}\n{traceback.format_exc()}")
            raise ex

    def upload(self, path: str, loader_params: dict = None, namespace: str = "default") -> List[str]:
        return self.sync(self.aupload(path, loader_params, namespace))

    async def adelete(self, id: str, namespace: str = "default"):
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.delete(
                    self.base_url + f"/document/{namespace}/{id}",
                    timeout=self.timeout
                ):
                    pass

        except Exception as ex:
            logger.error(f"Error at VSSClient.delete: {str(ex)}\n{traceback.format_exc()}")
            raise ex

    def delete(self, id: str, namespace: str = "default"):
        self.sync(self.adelete(id, namespace))

    async def adelete_all(self, namespace: str = "default"):
        try:
            async with aiohttp.ClientSession(raise_for_status=True) as client_session:
                async with client_session.delete(
                    self.base_url + f"/document/{namespace}/all",
                    timeout=self.timeout
                ):
                    pass

        except Exception as ex:
            logger.error(f"Error at VSSClient.delete_all: {str(ex)}\n{traceback.format_exc()}")
            raise ex

    def delete_all(self, namespace: str = "default"):
        self.sync(self.adelete_all(namespace))

    async def aload_records_as_json(self, path) -> List[dict]:
        async with aiofiles.open(path, mode="r", newline="") as file:
            content = await file.read()
            try:
                return json.loads(content)["records"]
            except Exception:
                csv_lines = content.split("\n")
                reader = csv.DictReader(csv_lines)
                return [dict(r) for r in reader]

    async def aimport_file(self, path: str, content_key: str = "page_content", namespace: str = "default") -> dict:
        records = await self.aload_records_as_json(path)

        ret = {"ids": [], "errors": []}
        for r in records:
            try:
                page_content = r[content_key]
                if "id" in r:
                    await self.aupdate([r["id"]], [Document(page_content=page_content, metadata=r)], namespace)
                    ret["ids"].append(r["id"])
                else:
                    ret["ids"].append((await self.aadd([Document(page_content=page_content, metadata=r)], namespace))[0])
            except Exception as ex:
                ret["errors"].append({"message": str(ex), "record": r})

        return ret

    def import_file(self, path: str, content_key: str = "content", namespace: str = "default") -> dict:
        return self.sync(self.aimport_file(path, content_key, namespace))
