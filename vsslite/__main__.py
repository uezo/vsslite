import os
import uvicorn
from vsslite import VSSLiteServer

vss = VSSLiteServer(os.getenv("OPENAI_APIKEY"), os.getenv("DATA_PATH"))
uvicorn.run(vss.app, host="0.0.0.0", port=8000)
