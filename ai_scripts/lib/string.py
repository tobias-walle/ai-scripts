from dataclasses import dataclass
import re
from typing import Optional


@dataclass
class ExtractedCode:
    code: str
    language: Optional[str]
    completed: bool


def extract_first_code_snippet_from_markdown(markdown: str) -> ExtractedCode:
    result = []
    in_markdown = False
    number_ticks = 0
    completed = False
    language = None
    for line in markdown.splitlines():
        if in_markdown:
            md_end_match = re.match(f"^(`{{{number_ticks}}}) *$", line)
            if md_end_match:
                completed = True
                break
            else:
                result.append(line)
        else:
            md_start_match = re.match(r"^(`{3,})(\w*) *$", line)
            if md_start_match is not None:
                in_markdown = True
                number_ticks = len(md_start_match.group(1))
                language = md_start_match.group(2)
    code = "\n".join(result)
    return ExtractedCode(code=code, completed=completed, language=language)
