import tiktoken
from tiktoken.core import Encoding


def number_of_tokens(text: str) -> int:
    return len(token_encoding().encode(text))


def limit_tokens(text: str, limit: int) -> str:
    encoding = token_encoding()
    tokens = encoding.encode(text)
    tokens = tokens[:limit]
    return encoding.decode(tokens)


def token_encoding() -> Encoding:
    return tiktoken.encoding_for_model("gpt-4-1106-preview")
