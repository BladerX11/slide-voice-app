"""SSML processing for custom slide syntax."""

import re
from abc import ABC, abstractmethod


class SSMLRule(ABC):
    """Base class for SSML transformation rules."""

    @abstractmethod
    def apply(self, text: str) -> str:
        """Apply the rule to the input text.

        Args:
            text: The input text to transform.

        Returns:
            The transformed text.
        """
        pass


class VoiceRule(SSMLRule):
    """Wrap paragraphs that start with [voice-name] in <voice> tags."""

    def __init__(self):
        self._pattern = re.compile(
            r"^\[(?P<voice>[^\]]+)\](?P<content>.*)(?P<ending>\r?\n)?$"
        )

    def apply(self, text: str) -> str:
        lines = text.splitlines(keepends=True)
        updated_lines: list[str] = []

        for line in lines:
            match = self._pattern.match(line)
            if match:
                groups = match.groupdict()
                updated_lines.append(
                    f'<voice name="{groups["voice"]}">{groups["content"]}</voice>{groups["ending"] or ""}'
                )
            else:
                updated_lines.append(line)

        return "".join(updated_lines)


class BreakRule(SSMLRule):
    """Convert dot runs surrounded by spaces to <break> tags."""

    def __init__(self):
        self._pattern = re.compile(r"(?<!\S)\.+(?!\S)")

    def apply(self, text: str) -> str:
        return self._pattern.sub(
            lambda match: f'<break time="{len(match.group(0))}s"/>', text
        )


class EmphasisRule(SSMLRule):
    """Convert _text_ to <emphasis level="strong">text</emphasis>."""

    def __init__(self):
        self._pattern = re.compile(r"(?<!\S)_(.+?)_(?!\S)")

    def apply(self, text: str) -> str:
        return self._pattern.sub(
            lambda match: f'<emphasis level="strong">{match.group(1)}</emphasis>',
            text,
        )


class SSMLProcessor:
    """Apply a sequence of SSML transformation rules."""

    def __init__(self):
        self._rules: list[SSMLRule] = [VoiceRule(), BreakRule(), EmphasisRule()]

    def to_ssml(self, text: str) -> str:
        """Convert custom syntax to SSML wrapped in <speak> tags.

        Args:
            text: The input text with custom syntax.

        Returns:
            The SSML-formatted text.
        """
        for rule in self._rules:
            text = rule.apply(text)
        return f"<speak>{text}</speak>"
