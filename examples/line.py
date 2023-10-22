import logging
import os
from vsslite.chatgpt_processor import VSSQAFunction
from vsslite.line import LineBotServer


YOUR_CHANNEL_ACCESS_TOKEN = ""
YOUR_CHANNEL_SECRET = ""


# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_format = logging.Formatter("%(asctime)s %(levelname)8s %(message)s")
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(log_format)
logger.addHandler(streamHandler)

# Setup QA function(s)
from vsslite.chatgpt_processor import VSSQAFunction
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

app = LineBotServer(
    channel_access_token=YOUR_CHANNEL_ACCESS_TOKEN,
    channel_secret=YOUR_CHANNEL_SECRET,
    endpoint_path="/linebot",   # <- Set "https://your_domain/linebot" to webhook url at LINE Developers
    functions=[openai_qa_func]
).app

# Invoke app (single process)
# uvicorn line:app --host 0.0.0.0 --port 8002
