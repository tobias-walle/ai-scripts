import os
from typing import (
    Iterable,
    List,
    NotRequired,
    Protocol,
    TypedDict,
    Unpack,
)

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class ChatOptions(TypedDict):
    max_tokens: NotRequired[int]
    temperature: NotRequired[float]
    top_p: NotRequired[float]
    presence_penalty: NotRequired[float]


class Model(Protocol):
    def complete(
        self,
        messages: List[ChatCompletionMessageParam],
        **kwargs: Unpack[ChatOptions],
    ) -> str:
        ...

    def stream(
        self,
        messages: List[ChatCompletionMessageParam],
        **kwargs: Unpack[ChatOptions],
    ) -> Iterable[str]:
        ...


class _OpenAICompatibleModel(Model, Protocol):
    def complete(self, messages, **kwargs):
        answer = self._client().chat.completions.create(
            model=self._model(),
            messages=messages,
            stream=False,
            **self._options(kwargs),
        )
        return answer.choices[0].message.content or ""

    def stream(self, messages, **kwargs):
        stream = self._client().chat.completions.create(
            model=self._model(),
            messages=messages,
            stream=True,
            **self._options(kwargs),
        )
        return (
            chunk.choices[0].delta.content
            for chunk in stream
            if chunk.choices[0].delta.content is not None
        )

    def _options(self, options) -> ChatOptions:
        return {
            "max_tokens": options.pop("max_tokens", 1024),
            "temperature": options.pop("temperature", 1),
            "top_p": options.pop("top_p", 1),
            "presence_penalty": options.pop("presence_penalty", 1),
        }

    def _model(self) -> str:
        ...

    def _client(self) -> OpenAI:
        ...


class TogetherAIMistral8x7BModel(_OpenAICompatibleModel):
    def _model(self):
        return "mistralai/Mixtral-8x7B-Instruct-v0.1"

    def _client(self):
        return _together_client()


class OpenAIGPT4TurboModel(_OpenAICompatibleModel):
    def _model(self):
        return "gpt-4-1106-preview"

    def _client(self):
        return _openai_client()


def _together_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("TOGETHER_API_TOKEN"),
        base_url="https://api.together.xyz/v1",
    )


def _openai_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
