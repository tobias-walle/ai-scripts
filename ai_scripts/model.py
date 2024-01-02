import os
from typing import List, Optional, Protocol, TypeVar

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class Model(Protocol):
    def chat(
        self,
        messages: List[ChatCompletionMessageParam],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        presence_penalty: Optional[float] = None,
    ) -> str:
        ...


class TogetherAIMistral8x7BModel(Model):
    def chat(
        self,
        messages,
        max_tokens=None,
        temperature=None,
        top_p=None,
        presence_penalty=None,
    ) -> str:
        answer = _together_client().chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=messages,
            max_tokens=_default_value(max_tokens, 1024),
            temperature=_default_value(temperature, 1),
            top_p=_default_value(top_p, 1),
            presence_penalty=_default_value(presence_penalty, 1),
        )
        return answer.choices[0].message.content or ""


class OpenAIGPT4TurboModel(Model):
    def chat(
        self,
        messages,
        max_tokens=None,
        temperature=None,
        top_p=None,
        presence_penalty=None,
    ) -> str:
        answer = _openai_client().chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            max_tokens=_default_value(max_tokens, 1024),
            temperature=_default_value(temperature, 1),
            top_p=_default_value(top_p, 1),
            presence_penalty=_default_value(presence_penalty, 1),
        )
        return answer.choices[0].message.content or ""


def _together_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("TOGETHER_API_TOKEN"),
        base_url="https://api.together.xyz/v1",
    )


def _openai_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )


T = TypeVar("T")


def _default_value(value: Optional[T], default: T) -> T:
    return default if value is None else value
