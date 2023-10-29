import os
from logging import getLogger
from typing import List
import streamlit as st

from .chatgpt_processor import (
    ChatGPTFunctionBase,
    ChatGPTProcessor
)


logger = getLogger(__name__)


class ChatUI:
    def __init__(
        self, *,
        apikey: str = None,
        api_base: str = None,
        api_type: str = None,
        api_version: str = None,
        model: str = "gpt-3.5-turbo-16k-0613",
        engine: str = None,
        temperature: float=1.0, max_tokens: int = 0, 
        functions: List[ChatGPTFunctionBase] = None,
        system_message_content: str = None,
        title: str = None, input_prompt: str = None
    ) -> None:
        self.apikey = apikey or os.environ.get("OPENAI_API_KEY")
        self.api_base = api_base
        self.api_type = api_type
        self.api_version = api_version
        self.model = model
        self.engine = engine
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.functions = functions or []
        self.system_message_content = system_message_content
        self.title = title or "VSSLite Chat v0.6.1"
        self.input_prompt = input_prompt or "Send a message"

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
            functions={
                func.name: func for func in self.functions
            },
            system_message_content=self.system_message_content
        )

    async def on_userinput(self, user_content: str):
        with st.chat_message("user"):
            st.markdown(user_content)
        st.session_state.messages.append({"role": "user", "content": user_content})

        with st.chat_message("assistant"):
            chat_processor = st.session_state.chat_processor
            temp_container = st.empty()
            assistant_content = ""
            async for t in chat_processor.chat(user_content):
                assistant_content += t
                temp_container.markdown(assistant_content + "▌")
            temp_container.markdown(assistant_content)
        st.session_state.messages.append({"role": "assistant", "content": assistant_content})

        st.session_state.clear_button_enabled = True

    async def start(self):
        st.title(self.title)

        # State variables
        if "chat_processor" not in st.session_state:
            st.session_state.chat_processor = self.create_processor()

        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "clear_button_enabled" not in st.session_state:
            st.session_state.clear_button_enabled = False

        # UI
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_content = st.chat_input(self.input_prompt)
        if user_content:
            await self.on_userinput(user_content)

        if st.session_state.clear_button_enabled:
            if st.button("Clear messages"):
                st.session_state.messages = []
                st.session_state.chat_processor.histories.clear()
                st.session_state.clear_button_enabled = False
                st.rerun()
