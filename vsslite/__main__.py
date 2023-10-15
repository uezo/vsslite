import os
import sys
import uvicorn

args = sys.argv

if len(args) > 1 and args[1] == "sqlite":
    from vsslite import VSSLiteServer
    vss = VSSLiteServer(os.getenv("OPENAI_APIKEY"), os.getenv("DATA_PATH"))

else:
    from vsslite import LangChainVSSLiteServer
    vss = LangChainVSSLiteServer(os.getenv("OPENAI_APIKEY"))

uvicorn.run(vss.app, host="0.0.0.0", port=8000)
