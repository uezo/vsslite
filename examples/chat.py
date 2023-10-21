import asyncio
import logging
import os
from vsslite.chat import (
    ChatUI,
    VSSQAFunction
)

YOUR_API_KEY = ""

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_format = logging.Formatter("%(asctime)s %(levelname)8s %(message)s")
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(log_format)
logger.addHandler(streamHandler)

# Setup QA function(s)
openai_qa_func = VSSQAFunction(
    name="get_openai_terms_of_use",
    description="Get information about terms of use of OpenAI services including ChatGPT.",
    parameters={"type": "object", "properties": {}},
    vss_url=os.getenv("VSS_URL") or "http://127.0.0.1:8000",
    namespace="openai",
    # answer_lang="Japanese",  # <- Uncomment if you want to get answer in Japanese
    # is_always_on=True,  # <- Uncomment if you want to always fire this function
    verbose=True
)

# Start app
chatui = ChatUI(
    apikey=YOUR_API_KEY or os.getenv("OPENAI_API_KEY"),
    temperature=0.5,
    functions=[openai_qa_func],
    # To use Azure OpenAI Service uncomment and configure below
    # api_type="azure",
    # api_base="https://your-endpoint.openai.azure.com/",
    # api_version="2023-08-01-preview",
    # engine="your-embeddings-deployment-name"
)
asyncio.run(chatui.start())

# Invoke app
# streamlit run chat.py --server.address=0.0.0.0 --server.port=8001
