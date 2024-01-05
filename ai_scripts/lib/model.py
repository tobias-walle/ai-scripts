from enum import Enum
import os
from typing import (
    Iterable,
    List,
    NotRequired,
    Optional,
    Protocol,
    TypedDict,
    Unpack,
)

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from ai_scripts.lib.logging import print_step


class ChatOptions(TypedDict):
    max_tokens: NotRequired[int]
    temperature: NotRequired[float]
    top_p: NotRequired[float]
    presence_penalty: NotRequired[float]


class Model(Protocol):
    name: str
    abbr: Optional[str]

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


class OpenAICompatibleModel(Model):
    def __init__(self, name: str, abbr: Optional[str], client: OpenAI) -> None:
        self.client = client
        self.name = name
        self.abbr = abbr

    def complete(self, messages, **kwargs):
        answer = self.client.chat.completions.create(
            model=self.name,
            messages=messages,
            stream=False,
            **self._options(kwargs),
        )
        return answer.choices[0].message.content or ""

    def stream(self, messages, **kwargs):
        stream = self.client.chat.completions.create(
            model=self.name,
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
            "max_tokens": options.pop("max_tokens", None),
            "temperature": options.pop("temperature", None),
            "top_p": options.pop("top_p", None),
            "presence_penalty": options.pop("presence_penalty", None),
        }

    def _model(self) -> str:
        ...

    def _client(self) -> OpenAI:
        ...


def _together_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("TOGETHER_API_TOKEN"),
        base_url="https://api.together.xyz/v1",
    )


def _openai_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )


class Models(Enum):
    GPT_4_TURBO = OpenAICompatibleModel("gpt-4-1106-preview", "G4", _openai_client())
    MIXTRAL_8_7B = OpenAICompatibleModel(
        "mistralai/Mixtral-8x7B-Instruct-v0.1", "MX8", _together_client()
    )
    MISTRAL_7B = OpenAICompatibleModel(
        "mistralai/Mistral-7B-Instruct-v0.2", "MS7", _together_client()
    )

    @classmethod
    def get_by_name(
        cls, name: Optional[str], default_model: Optional[Model] = None
    ) -> Model:
        if name is None or name == "":
            return default_model or cls.GPT_4_TURBO.value
        lname = name.lower()
        for enum in cls:
            m = enum.value
            if m.name.lower() == lname or (
                m.abbr is not None and m.abbr.lower() == lname
            ):
                return m
        print_step(
            f'Couldn\'t find model "{name}". Try to access it anyway on TogetherAI.'
        )
        return OpenAICompatibleModel(name, None, _together_client())
