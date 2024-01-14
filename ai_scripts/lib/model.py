from enum import Enum
import os
from typing import (
    Iterable,
    List,
    Literal,
    NotRequired,
    Optional,
    Protocol,
    Required,
    TypedDict,
    Unpack,
)
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from ai_scripts.lib.logging import print_status, print_step


class Message(TypedDict):
    content: Required[str]
    role: Required[Literal["system"] | Literal["user"] | Literal["assistant"]]


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
        messages: List[Message],
        **kwargs: Unpack[ChatOptions],
    ) -> str:
        ...

    def stream(
        self,
        messages: List[Message],
        **kwargs: Unpack[ChatOptions],
    ) -> Iterable[str]:
        ...


class OpenAICompatibleModel(Model):
    def __init__(self, name: str, abbr: Optional[str], client: OpenAI) -> None:
        self.client = client
        self.name = name
        self.abbr = abbr

    def complete(self, messages, **kwargs):
        print_status(f"Using {self.name}")
        answer = self.client.chat.completions.create(
            model=self.name,
            messages=self.map_messages(messages),
            stream=False,
            **kwargs,
        )
        return answer.choices[0].message.content or ""

    def stream(self, messages, **kwargs):
        print_status(f"Using {self.name} (stream)")
        stream = self.client.chat.completions.create(
            model=self.name,
            messages=self.map_messages(messages),
            stream=True,
            **kwargs,
        )
        return (
            chunk.choices[0].delta.content
            for chunk in stream
            if chunk.choices[0].delta.content is not None
        )

    def map_messages(self, messages: List[Message]) -> List[ChatCompletionMessageParam]:
        result: List[ChatCompletionMessageParam] = []
        for m in messages:
            if m["role"] == "system":
                result.append({"role": "system", "content": m["content"]})
            if m["role"] == "user":
                result.append({"role": "user", "content": m["content"]})
            if m["role"] == "assistant":
                result.append({"role": "assistant", "content": m["content"]})
        return result


class LangchainModel(Model):
    def __init__(
        self, name: str, abbr: Optional[str], base_model: BaseChatModel
    ) -> None:
        self.name = name
        self.abbr = abbr
        self.base_model = base_model

    def complete(self, messages, **kwargs) -> str:
        print_status(f"Using {self.name}")
        answer = self.base_model.invoke(self.map_messages(messages), **kwargs)
        return str(answer.content)

    def stream(self, messages, **kwargs) -> Iterable[str]:
        print_status(f"Using {self.name} (stream)")
        stream = self.base_model.stream(self.map_messages(messages), **kwargs)
        return (str(chunk.content) for chunk in stream)

    def map_messages(self, messages: List[Message]) -> LanguageModelInput:
        result: LanguageModelInput = []
        for m in messages:
            if m["role"] == "system":
                result.append(SystemMessage(content=m["content"]))
            if m["role"] == "user":
                result.append(HumanMessage(content=m["content"]))
            if m["role"] == "assistant":
                result.append(AIMessage(content=m["content"]))
        return result


def openai_model(name: str, abbr: Optional[str]) -> Model:
    return OpenAICompatibleModel(
        name,
        abbr,
        OpenAI(),
    )


def mistralai_model(name: str, abbr: Optional[str]) -> Model:
    return OpenAICompatibleModel(
        name,
        abbr,
        OpenAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1",
        ),
    )


def togetherai_model(name: str, abbr: Optional[str]) -> Model:
    return OpenAICompatibleModel(
        name,
        abbr,
        OpenAI(
            api_key=os.getenv("TOGETHER_API_KEY"),
            base_url="https://api.together.xyz/v1",
        ),
    )


def ollama_model(model: str, name: str, abbr: Optional[str]) -> Model:
    return LangchainModel(
        name,
        abbr,
        ChatOllama(
            base_url="http://localhost:11434",
            model=model,
        ),
    )


class Models(Enum):
    GPT_4_TURBO = openai_model("gpt-4-1106-preview", "G4")
    MIXTRAL_8_7B = togetherai_model("mistralai/Mixtral-8x7B-Instruct-v0.1", "M8")
    MISTRAL_7B = togetherai_model("mistralai/Mistral-7B-Instruct-v0.2", "M7")
    MISTRAL_TINY = mistralai_model("mistral-tiny", "MT")
    MISTRAL_SMALL = mistralai_model("mistral-small", "MS")
    MISTRAL_MEDIUM = mistralai_model("mistral-medium", "MM")

    OLLAMA_MISTRAL_7B = ollama_model(
        "mistral:7b-instruct",
        "ollama/mistral:7b-instruct",
        "OM7",
    )

    @classmethod
    def get_from_env_or_default(cls, default_model: Optional[Model] = None) -> Model:
        name = os.getenv("MODEL", None)
        if name is None or name == "":
            return default_model or cls.GPT_4_TURBO.value
        return cls.get_by_name(name)

    @classmethod
    def get_by_name(cls, name: str) -> Model:
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
        return togetherai_model(name, None)
