import json
import os
import pytest
from vsslite.chatgpt_processor import ChatGPTProcessor, ChatGPTFunctionBase, ChatGPTFunctionResponse

API_KEY = os.environ.get("OPENAI_APIKEY")


@pytest.mark.asyncio
async def test_chat():
    chat_processor = ChatGPTProcessor()

    response_text = ""
    async for t in chat_processor.chat("こんにちは。あなたもこんにちはと言ってください。"):
        response_text += t
    
    assert "こんにちは" in response_text


@pytest.mark.asyncio
async def test_chat_with_func():
    class WeatherFunc(ChatGPTFunctionBase):
        name = "get_weather"
        description = "天気を取得します"
        parameters = {"type": "object", "properties": {"location": {"type": "string"}}}
        is_always_on = False

        async def aexecute(self, request_text: str, **kwargs) -> ChatGPTFunctionResponse:
            return ChatGPTFunctionResponse(json.dumps({"weather": "晴れ", "temperature": 30}))
    
    chat_processor = ChatGPTProcessor(functions={"get_weather": WeatherFunc()})

    response_text = ""
    async for t in chat_processor.chat("東京の天気は？"):
        response_text += t
    
    assert "晴" in response_text
    assert "30" in response_text
