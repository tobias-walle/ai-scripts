from typing import Iterable, List, Unpack

from openai.types.chat import ChatCompletionMessageParam
from ai_scripts.lib.model import ChatOptions, Model


class Agent:
    def __init__(
        self, model: Model, system_prompt: str, **options: Unpack[ChatOptions]
    ) -> None:
        self.model = model
        self.system_prompt = system_prompt
        self.options = options

    def complete(self, user_prompt: str) -> str:
        return self.model.complete(
            messages=self._messages(user_prompt),
            **self.options,
        )

    def stream(self, user_prompt: str) -> Iterable[str]:
        return self.model.stream(
            messages=self._messages(user_prompt),
            **self.options,
        )

    def _messages(self, user_prompt: str) -> List[ChatCompletionMessageParam]:
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]
