"""Converters for transforming message formats.

This module contains compatibility helpers to convert legacy Chat Completions
messages into the OpenAI Responses API input format. Keeping these utilities in
their own namespace avoids confusion with methods on core types like
`StructuredPrompt`.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict, cast


class ResponsesPart(TypedDict):
    type: Literal["input_text"]
    text: str


class ResponsesMessage(TypedDict):
    role: str
    content: list[ResponsesPart]


def convert_chat_messages_to_responses_input(
    messages: list[dict[str, Any]], map_system_to_developer: bool = True
) -> list[ResponsesMessage]:
    """Convert legacy Chat Completions-style messages to Responses API input.

    Accepted message shapes include:
    - {"role": "...", "content": "string"}
    - {"role": "...", "content": [{"type": "text", "text": "..."}, ...]}
    - {"role": "...", "content": [{"type": "input_text", "text": "..."}, ...]}

    Args:
        messages: The list of legacy messages.
        map_system_to_developer: When True, map any "system" role to "developer".

    Returns:
        list[ResponsesMessage]: Messages formatted for the Responses API.
    """

    def _coerce_parts(value: object) -> list[ResponsesPart]:
        if isinstance(value, list):
            normalized: list[ResponsesPart] = []
            for part in cast(list[Any], value):
                if isinstance(part, dict):
                    part_dict = cast(dict[str, Any], part)
                    if part_dict.get("type") == "input_text" and "text" in part_dict:
                        text_value = part_dict.get("text")
                        normalized.append(
                            {
                                "type": "input_text",
                                "text": "" if text_value is None else str(text_value),
                            }
                        )
                    elif part_dict.get("type") == "text" and "text" in part_dict:
                        text_value = part_dict.get("text")
                        normalized.append(
                            {
                                "type": "input_text",
                                "text": "" if text_value is None else str(text_value),
                            }
                        )
                    else:
                        normalized.append(
                            {"type": "input_text", "text": str(cast(object, part))}
                        )
                else:
                    normalized.append(
                        {"type": "input_text", "text": str(cast(object, part))}
                    )
            return normalized if normalized else [{"type": "input_text", "text": ""}]
        return [{"type": "input_text", "text": "" if value is None else str(value)}]

    converted: list[ResponsesMessage] = []
    for m in messages:
        role = str(m.get("role", "user")).lower()
        if map_system_to_developer and role == "system":
            role = "developer"
        content_value = m.get("content")
        converted.append({"role": role, "content": _coerce_parts(content_value)})

    return converted
