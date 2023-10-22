import aiohttp
from logging import getLogger
import os
import traceback
from typing import List
from uuid import uuid4

from linebot import AsyncLineBotApi, WebhookParser
from linebot.aiohttp_async_http_client import AiohttpAsyncHttpClient
from linebot.models import (
    MessageEvent, TextSendMessage,
    PostbackEvent, PostbackAction,
    QuickReply, QuickReplyButton
)
from fastapi import FastAPI, Request, BackgroundTasks

from vsslite.chatgpt_processor import ChatGPTProcessor, ChatGPTFunctionBase


logger = getLogger(__name__)


class StreamBuffer:
    def __init__(self, text: str = None, is_done: bool = False):
        self.id = str(uuid4())
        self.text = text or ""
        self.is_done = is_done

    def pop(self):
        if self.is_done:
            return self.text
        
        pop_pos = max(self.text.rfind("。"), self.text.rfind("\n")) + 1
        pop_text = ""
        if pop_pos > 0:
            pop_text = self.text[:pop_pos]
            self.text = self.text[pop_pos:]
        return pop_text.strip("\n")


class LineBotServer:
    def __init__(self, *,
        apikey: str = None,
        api_base: str = None,
        api_type: str = None,
        api_version: str = None,
        model: str = "gpt-3.5-turbo-16k-0613",
        engine: str = None,
        temperature: float = 1.0,
        max_tokens: int = 0, 
        functions: List[ChatGPTFunctionBase] = None,
        system_message_content: str = None,
        endpoint_path: str = "/linebot",
        channel_access_token: str = None,
        channel_secret: str = None,
        reply_length_threshold: int = 150,
        server_args: dict = None
    ):
        # ChatGPT
        self.apikey = apikey or os.environ.get("OPENAI_API_KEY")
        self.api_base = api_base
        self.api_type = api_type
        self.api_version = api_version
        self.model = model
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.functions = {
            func.name: func for func in functions or []
        }
        self.system_message_content = system_message_content

        # LINE
        self.endpoint_path = endpoint_path
        self.channel_access_token = channel_access_token or os.getenv("LINE_ACCESS_TOKEN")
        self.channel_secret = channel_secret or os.getenv("LINE_SECRET")
        self.reply_length_threshold = reply_length_threshold
        self.session = aiohttp.ClientSession()
        client = AiohttpAsyncHttpClient(self.session)
        self.line_api = AsyncLineBotApi(
            channel_access_token=channel_access_token,
            async_http_client=client
        )
        self.parser = WebhookParser(channel_secret=channel_secret)
        self.chat_processors = {}
        self.stream_buffers = {}

        # FastAPI Server
        self.app = FastAPI(**(server_args or {}))
        self.setup_handlers()

    def setup_handlers(self):
        app = self.app

        @app.on_event("shutdown")
        async def app_shutdown():
            await self.session.close()

        @app.post(self.endpoint_path)
        async def handle_request(request: Request, background_tasks: BackgroundTasks):
            events = self.parser.parse(
                (await request.body()).decode("utf-8"),
                request.headers.get("X-Line-Signature", "")
            )
            background_tasks.add_task(self.handle_events, events=events)
            return "ok"


    async def reply_from_buffer(self, reply_token: str, user_id: str) -> bool:
        stream_buffer = self.stream_buffers[user_id]
        reply_text = stream_buffer.pop()

        if reply_text:
            reply_message = TextSendMessage(text=reply_text)

            if stream_buffer.is_done:
                del self.stream_buffers[user_id]

            else:
                reply_message.quick_reply = QuickReply(items=[
                    QuickReplyButton(
                        action=PostbackAction(label="続きを見る", data="continue")
                    )
                ])

            await self.line_api.reply_message(reply_token, reply_message)
            return True

        else:
            return False

    def create_processor(self):
        return  ChatGPTProcessor(
            api_key=self.apikey,
            api_base=self.api_base,
            api_type=self.api_type,
            api_version=self.api_version,
            model=self.model,
            engine=self.engine,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            functions=self.functions,
            system_message_content=self.system_message_content
        )

    async def handle_events(self, events):
        for ev in events:
            user_id = ev.source.user_id
            reply_token = ev.reply_token
            chat_processor = self.chat_processors.get(user_id)
            if not chat_processor:
                chat_processor = self.create_processor()
                self.chat_processors[user_id] = chat_processor

            if isinstance(ev, PostbackEvent):
                if ev.postback.data == "continue":
                    await self.reply_from_buffer(reply_token, user_id)

            elif isinstance(ev, MessageEvent):
                try:
                    stream_buffer = StreamBuffer()
                    self.stream_buffers[user_id] = stream_buffer
                    is_reply_sent = False
                    async for t in chat_processor.chat(ev.message.text):
                        if stream_buffer.id != self.stream_buffers[user_id].id:
                            # Break(stop chat_processor.chat) if other thread overwrite stream_buffer
                            is_reply_sent = True
                            break

                        stream_buffer.text += t
                        if not is_reply_sent and len(stream_buffer.text) > self.reply_length_threshold:
                            is_reply_sent = await self.reply_from_buffer(reply_token, user_id)

                    stream_buffer.is_done = True

                    if not is_reply_sent:
                        await self.reply_from_buffer(reply_token, user_id)

                except Exception as ex:
                    logger.error(f"Chat error: {ex}\n{traceback.format_exc()}")
                    await  self.line_api.reply_message(reply_token, TextSendMessage(text="😣"))
                    del self.stream_buffers[user_id]
