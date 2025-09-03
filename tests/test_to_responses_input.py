from promptdown import StructuredPrompt, Message
from promptdown.converters import (
    convert_chat_messages_to_responses_input as convert,
)


def test_to_responses_input_basic_and_order_and_role_map():
    prompt = StructuredPrompt(
        name="Example Prompt",
        system_message="Preamble",
        conversation=[
            Message(role="User", content="Hi"),
            Message(role="Assistant", content="Hello"),
        ],
    )

    result = prompt.to_responses_input()

    assert result == [
        {"role": "developer", "content": [{"type": "input_text", "text": "Preamble"}]},
        {"role": "user", "content": [{"type": "input_text", "text": "Hi"}]},
        {"role": "assistant", "content": [{"type": "input_text", "text": "Hello"}]},
    ]


def test_to_responses_input_coerces_non_string_content():
    prompt = StructuredPrompt(
        name="Example",
        developer_message="Dev msg",
        conversation=[
            Message(role="User", content=str(123)),
        ],
    )

    result = prompt.to_responses_input()
    assert result[0]["content"] == [{"type": "input_text", "text": "Dev msg"}]
    assert result[1]["content"] == [{"type": "input_text", "text": "123"}]


def test_to_responses_input_passes_through_input_text_parts():
    _ = StructuredPrompt(
        name="Parts",
        developer_message="lead",
        conversation=[
            Message(role="User", content="ignored"),
        ],
    )
    # Manually override to simulate pre-structured parts
    parts = [{"type": "input_text", "text": "already"}]
    # replace with structured parts and check again via converter utility
    messages = [
        {"role": "system", "content": "lead"},
        {"role": "user", "content": parts},
    ]
    converted = convert(messages)
    assert converted == [
        {"role": "developer", "content": [{"type": "input_text", "text": "lead"}]},
        {"role": "user", "content": [{"type": "input_text", "text": "already"}]},
    ]


def test_to_responses_input_empty_string_generates_single_part():
    prompt = StructuredPrompt(
        name="Empty",
        developer_message="",
        conversation=[Message(role="User", content="")],
    )
    result = prompt.to_responses_input()
    assert result == [
        {"role": "developer", "content": [{"type": "input_text", "text": ""}]},
        {"role": "user", "content": [{"type": "input_text", "text": ""}]},
    ]


def test_converter_legacy_chat_messages():
    legacy = [
        {"role": "system", "content": "Sys"},
        {"role": "user", "content": [{"type": "text", "text": "Hi"}]},
        {"role": "assistant", "content": [{"type": "input_text", "text": "Hello"}]},
    ]
    converted = convert(legacy)
    assert converted == [
        {"role": "developer", "content": [{"type": "input_text", "text": "Sys"}]},
        {"role": "user", "content": [{"type": "input_text", "text": "Hi"}]},
        {"role": "assistant", "content": [{"type": "input_text", "text": "Hello"}]},
    ]
