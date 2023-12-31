# Check SQLite version to satisfy ChromaDB requirements
import sqlite3
if sqlite3.sqlite_version_info < (3, 35, 0):
    import sys
    try:
        __import__("pysqlite3")
    except ImportError:
        import subprocess
        print("Start installing additional dependencies for ChromaDB ...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pysqlite3-binary"]
        )
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import logging
import os
from vsslite import LangChainVSSLiteServer

YOUR_API_KEY = ""

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_format = logging.Formatter("%(asctime)s %(levelname)8s %(message)s")
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(log_format)
logger.addHandler(streamHandler)

# Configure app
from vsslite import LangChainVSSLiteServer

# To use Azure OpenAI Service uncomment and configure below
# from langchain.embeddings import OpenAIEmbeddings
# azure_embeddings = OpenAIEmbeddings(
#     openai_api_type="azure",
#     openai_api_base="https://your-endpoint.openai.azure.com/",
#     openai_api_version="2023-08-01-preview",
#     deployment="your-embeddings-deployment-name"
# )

app = LangChainVSSLiteServer(
    apikey=YOUR_API_KEY or os.getenv("OPENAI_API_KEY"),
    persist_directory="./vectorstore",
    chunk_size=500,
    chunk_overlap=0,
    # embedding_function=azure_embeddings   # <- Uncomment to use Azure OpenAI Service
).app

# Invoke app (single process)
# uvicorn api:app --host 0.0.0.0 --port 8000

# Invoke app (multi process)
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:8000 
