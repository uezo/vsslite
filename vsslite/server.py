from logging import getLogger
import traceback
from typing import List, Optional
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from .vsslite import VSSLite

logger = getLogger(__name__)


# API Schemas
class AddRequest(BaseModel):
    body: str = Field(..., title="body", description="Body for embedding", example="Eels and conger eels are both long, thin fish, but the difference is that eels are freshwater fish and conger eels are saltwater fish.")
    data: Optional[dict] = Field(None, title="data", description="Knowlegde data as JSON", example={"body": "Eels and conger eels are both long, thin fish, but the difference is that eels are freshwater fish and conger eels are saltwater fish.", "url": "https://~~~~"})


class AddResponse(BaseModel):
    id: int = Field(..., title="id", description="Record id", example=3)


class UpdateReqeust(AddRequest):
    pass


class UpdateResponse(AddResponse):
    pass


class Knowledge(BaseModel):
    id: int = Field(..., title="id", description="Record id", example=3)
    updated_at: str = Field(..., title="updated_at", description="Updated timestamp", example="2023-08-11T12:34:56Z")
    namespace: str = Field(..., title="namespace", description="Namespace this record belongs to", example="fishes")
    body: str = Field(..., title="body", description="Body for embedding", example="Eels and conger eels are both long, thin fish, but the difference is that eels are freshwater fish and conger eels are saltwater fish.")
    data: Optional[dict] = Field(None, title="data", description="Knowlegde data as JSON", example={"body": "Eels and conger eels are both long, thin fish, but the difference is that eels are freshwater fish and conger eels are saltwater fish.", "url": "https://~~~~"})


class GetResponse(Knowledge):
    body_embedding: list = Field(..., title="body_embedding", description="Vector data")


class SearchResult(Knowledge):
    distance: float = Field(..., title="distance", description="Distance")


class SearchResponse(BaseModel):
    results: List[SearchResult] = Field(..., title="results", description="Search results")


class ApiResponse(BaseModel):
    message: str = Field(..., title="message", description="Message from API", example="Embeddings created successfully")


# API router
class VSSLiteServer:
    def __init__(self, openai_apikey: str, connection_str: str="vss.db", server_args: dict=None):
        self.vssengine = VSSLite(
            openai_apikey=openai_apikey,
            connection_str=connection_str
        )
        self.vssengine.create_tables()
        self.app = FastAPI(**(server_args or {"title": "VSSLite API", "version": "0.1.0"}))
        self.setup_handlers()

    def setup_handlers(self):
        app = self.app

        @app.get("/knowledge/{namespace}/search", response_model=SearchResponse, tags=["Vector Similarity Search"])
        async def search_knowledge(q: str, namespace: str, count: int=1):
            try:
                results = []
                for r in await self.vssengine.asearch(q, count, namespace):
                    results.append(
                        SearchResult(
                            id=r["id"],
                            updated_at=r["updated_at"],
                            namespace=r["namespace"],
                            body=r["body"],
                            data=r["data"],
                            distance=r["distance"]
                        )
                    )
                return SearchResponse(results=results)

            except Exception as ex:
                logger.error(f"Error at vssengine.search_knowledge: {ex}\n{traceback.format_exc()}")
                return JSONResponse({"error": "Internal server error"}, 500)

        @app.post("/knowledge/{namespace}", response_model=AddResponse, tags=["Data management"])
        async def add_knowledge(namespace: str, request: AddRequest):
            try:
                id = await self.vssengine.aadd(request.body, request.data, namespace)
                return AddResponse(id=id)
            
            except Exception as ex:
                logger.error(f"Error at vssengine.add: {ex}\n{traceback.format_exc()}")
                return JSONResponse({"error": "Internal server error"}, 500)

        @app.patch("/knowledge/{id}", response_model=UpdateResponse, tags=["Data management"])
        async def update_knowledge(id: int, request: UpdateReqeust):
            try:
                r = await self.vssengine.aget(id)
                if not r:
                    return JSONResponse({"error": f"Id={id} not found"}, 404)
                
                new_id = await self.vssengine.aupdate(id, request.body, request.data)
                return UpdateResponse(id=new_id)
            
            except Exception as ex:
                logger.error(f"Error at vssengine.update: {ex}\n{traceback.format_exc()}")
                return JSONResponse({"error": "Internal server error"}, 500)

        @app.delete("/knowledge/all", response_model=ApiResponse, tags=["Data management"])
        async def delete_all_knowledge():
            try:
                await self.vssengine.adelete_all()
                return ApiResponse(message="Success")

            except Exception as ex:
                logger.error(f"Error at vssengine.delete_all: {ex}\n{traceback.format_exc()}")
                return JSONResponse({"error": "Internal server error"}, 500)

        @app.delete("/knowledge/{id}", response_model=ApiResponse, tags=["Data management"])
        async def delete_knowledge(id: int):
            try:
                await self.vssengine.adelete(id)
                return ApiResponse(message="Success")
            
            except Exception as ex:
                logger.error(f"Error at vssengine.delete: {ex}\n{traceback.format_exc()}")
                return JSONResponse({"error": "Internal server error"}, 500)

        @app.get("/knowledge/{id}", response_model=GetResponse, tags=["Data management"])
        async def get_knowledge(id: int):
            try:
                r = await self.vssengine.aget(id)
                if not r:
                    return JSONResponse({"error": f"Id={id} not found"}, 404)

                return GetResponse(
                    id=r["id"],
                    updated_at=r["updated_at"],
                    namespace=r["namespace"],
                    body=r["body"],
                    data=r["data"],
                    body_embedding=r["body_embedding"]
                )

            except Exception as ex:
                logger.error(f"Error at vssengine.get_knowledge: {ex}\n{traceback.format_exc()}")
                return JSONResponse({"error": "Internal server error"}, 500)
