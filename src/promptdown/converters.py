"""Converters for transforming message formats.

This module contains compatibility helpers to convert legacy Chat Completions
messages into the OpenAI Responses API input format. Keeping these utilities in
their own namespace avoids confusion with methods on core types like
`StructuredPrompt`.
"""

from __future__ import annotations

from typing import Any, cast
from .types import ResponsesMessage, ResponsesPart, Role


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
        map_system_to_developer: When True, map any "system" role to
            "developer".

    Returns:
        list[ResponsesMessage]: Messages formatted for the Responses API.
    """

    def normalize_role(raw_role: object) -> Role:
        role_value = str(raw_role if raw_role is not None else "user").lower()
        if map_system_to_developer:
            role_value = role_value.replace("system", "developer")
        return cast(Role, role_value)

    return [
        {
            "role": normalize_role(m.get("role", "user")),
            "content": coerce_to_response_parts(m.get("content")),
        }
        for m in messages
    ]


def coerce_to_response_parts(value: object) -> list[ResponsesPart]:
    """
    Coerce a message content value into a list of ResponsesPart objects.

    Args:
        value: The message content, which can be a string, a list of parts, or
            other types.

    Returns:
        list[ResponsesPart]: A list of well-formed ResponsesPart objects.
    """
    if isinstance(value, list):
        normalized: list[ResponsesPart] = []
        for part in cast(list[Any], value):
            if isinstance(part, dict):
                part_dict = cast(dict[str, Any], part)
                if part_dict.get("type") == "input_text" and "text" in (
                    part_dict
                ):
                    text_value = part_dict.get("text")
                    text = "" if text_value is None else str(text_value)
                    normalized.append(
                        {
                            "type": "input_text",
                            "text": text,
                        }
                    )
                elif part_dict.get("type") == "text" and "text" in part_dict:
                    text_value = part_dict.get("text")
                    text = "" if text_value is None else str(text_value)
                    normalized.append(
                        {
                            "type": "input_text",
                            "text": text,
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
        if normalized:
            return normalized
        return [{"type": "input_text", "text": ""}]
    text = "" if value is None else str(value)
    return [{"type": "input_text", "text": text}]
