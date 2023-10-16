import os
import json
from logging import getLogger
import traceback
from typing import Iterator, List

import streamlit as st
from openai import ChatCompletion


logger = getLogger(__name__)


class ChatGPTFunctionResponse:
    def __init__(self, content: str, role: str = "function") -> None:
        self.content = content
        self.role = role


class ChatGPTFunctionBase:
    name = None
    description = None
    parameters = {"type": "object", "properties": {}}
    
    def get_spec(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

    async def aexecute(self, request_text: str, **kwargs) -> ChatGPTFunctionResponse:
        pass


class ChatCompletionStreamResponse:
    def __init__(self, stream: Iterator[str], function_name: str=None):
        self.stream = stream
        self.function_name = function_name

    @property
    def response_type(self):
        return "function_call" if self.function_name else "content"


class ChatGPTProcessor:
    def __init__(self, api_key: str=None, model: str="gpt-3.5-turbo-16k-0613", temperature: float=1.0, max_tokens: int=0, functions: dict=None, system_message_content: str=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.functions = functions or {}
        self.system_message_content = system_message_content
        self.histories = []
        self.history_count = 20

    async def chat_completion_stream(self, messages, temperature: float = None, call_functions: bool=True):
        params = {
            "api_key": self.api_key,
            "messages": messages,
            "model": self.model,
            "temperature": self.temperature if temperature is None else temperature,
            "stream": True,
        }
        if self.max_tokens:
            params["max_tokens"] = self.max_tokens

        if call_functions and self.functions:
            params["functions"] = [v.get_spec() for _, v in self.functions.items()]

        stream_resp = ChatCompletionStreamResponse(await ChatCompletion.acreate(**params))

        async for chunk in stream_resp.stream:
            if chunk:
                delta = chunk["choices"][0]["delta"]
                if delta.get("function_call"):
                    stream_resp.function_name = delta["function_call"]["name"]
                break
        
        return stream_resp

    async def chat(self, text: str) -> Iterator[str]:
        try:
            messages = []
            if self.system_message_content:
                messages.append({"role": "system", "content": self.system_message_content})
            messages.extend(self.histories[-1 * self.history_count:])
            messages.append({"role": "user", "content": text})

            response_text = ""
            stream_resp = await self.chat_completion_stream(messages)

            async for chunk in stream_resp.stream:
                delta = chunk["choices"][0]["delta"]
                if stream_resp.response_type == "content":
                    content = delta.get("content")
                    if content:
                        response_text += delta["content"]
                        yield content

                elif stream_resp.response_type == "function_call":
                    function_call = delta.get("function_call")
                    if function_call:
                        arguments = function_call["arguments"]
                        response_text += arguments

            if stream_resp.response_type == "function_call":
                self.histories.append(messages[-1])
                self.histories.append({
                    "role": "assistant",
                    "function_call": {
                        "name": stream_resp.function_name,
                        "arguments": response_text
                    },
                    "content": None
                })

                function_resp = await self.functions[stream_resp.function_name].aexecute(text, **json.loads(response_text))

                if function_resp.role == "function":
                    messages.append({"role": "function", "content": json.dumps(function_resp.content), "name": stream_resp.function_name})
                else:
                    messages.append({"role": "user", "content": function_resp.content})

                response_text = ""
                stream_resp = await self.chat_completion_stream(messages, temperature=0, call_functions=False)

                async for chunk in stream_resp.stream:
                    delta = chunk["choices"][0]["delta"]
                    content = delta.get("content")
                    if content:
                        response_text += content
                        yield content
                
            if response_text:
                self.histories.append(messages[-1])
                self.histories.append({"role": "assistant", "content": response_text})

        except Exception as ex:
            logger.error(f"Error at chat: {str(ex)}\n{traceback.format_exc()}")
            raise ex


class ChatUI:
    def __init__(
        self, apikey: str = None, model: str="gpt-3.5-turbo-16k-0613",
        temperature: float=1.0, max_tokens: int=0, 
        functions: List[ChatGPTFunctionBase] = None,
        system_message_content: str=None,
        title: str = None, input_prompt: str = None
    ) -> None:
        self.apikey = apikey or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.functions = functions or []
        self.system_message_content = system_message_content
        self.title = title or "VSSLite Chat v0.4.0"
        self.input_prompt = input_prompt or "Send a message"

    def create_processor(self):
        return  ChatGPTProcessor(
            self.apikey,
            model=self.model,
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
