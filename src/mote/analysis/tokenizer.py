import re
from collections.abc import Iterator

from mote.analysis.models import Token


WORD_PATTERN = re.compile(r"\w+")

class Tokenizer:
    def tokenize(self, text: str) -> Iterator[Token]:
        for position, match in enumerate(WORD_PATTERN.finditer(text)):
            yield Token(
                term=match.group().casefold(),
                position=position,
                start_offset=match.start(),
                end_offset=match.end(),
            )