from promptdown import StructuredPrompt, Message


def test_from_promptdown_string_without_names():
    promptdown_string = "\n".join(
        [
            "",
            "# Example Prompt",
            "",
            "## System Message",
            "",
            "You are a helpful assistant.",
            "",
            "You should try to provide clear and concise answers to the "
            "user's questions.",
            "",
            "## Conversation",
            "",
            "**User:**",
            "Hi, can you help me?",
            "",
            "**Assistant:**",
            "Of course! What do you need assistance with?",
            "",
            "**User:**",
            "I'm having trouble with my code.",
            "",
            "**Assistant:**",
            "I'd be happy to help. What seems to be the problem?",
            "",
            "**User:**",
            'I\'m getting an error message that says "undefined variable".',
            "",
            "**Assistant:**",
            "That error usually occurs when you try to use a variable that "
            "hasn't been declared or assigned a value. Can you show me the "
            "code where you're encountering this error?",
            "",
        ]
    )

    expected_prompt = StructuredPrompt(
        name="Example Prompt",
        system_message=(
            "You are a helpful assistant.\n"
            "You should try to provide clear and concise answers to the "
            "user's questions."
        ),
        conversation=[
            Message(role="User", content="Hi, can you help me?"),
            Message(
                role="Assistant",
                content="Of course! What do you need assistance with?",
            ),
            Message(role="User", content="I'm having trouble with my code."),
            Message(
                role="Assistant",
                content="I'd be happy to help. What seems to be the problem?",
            ),
            Message(
                role="User",
                content=(
                    "I'm getting an error message that says "
                    '"undefined variable".'
                ),
            ),
            Message(
                role="Assistant",
                content=(
                    "That error usually occurs when you try to use a variable "
                    "that hasn't been declared or assigned a value. Can you "
                    "show me the code where you're encountering this error?"
                ),
            ),
        ],
    )

    prompt = StructuredPrompt.from_promptdown_string(promptdown_string)
    assert prompt is not None
    assert isinstance(prompt, StructuredPrompt)
    assert prompt.name == expected_prompt.name
    assert prompt.system_message == expected_prompt.system_message
    assert prompt.conversation == expected_prompt.conversation


def test_from_promptdown_string_with_names():
    promptdown_string = """
# Example Prompt

## System Message

You are a helpful assistant.

## Conversation

**User:**
Hi, can you help me?

**Assistant (Bot Friend):**
Of course! What do you need assistance with?

**User (Alice):**
I'm having trouble with my code.
"""

    expected_prompt = StructuredPrompt(
        name="Example Prompt",
        system_message="You are a helpful assistant.",
        conversation=[
            Message(role="User", content="Hi, can you help me?"),
            Message(
                role="Assistant",
                content="Of course! What do you need assistance with?",
                name="Bot Friend",
            ),
            Message(
                role="User",
                content="I'm having trouble with my code.",
                name="Alice",
            ),
        ],
    )

    prompt = StructuredPrompt.from_promptdown_string(promptdown_string)
    assert prompt == expected_prompt


def test_from_promptdown_string_with_simplified_conversation_format():
    promptdown_string = """
# Test Prompt

## System Message

This is a test system message.

This is a second line of the system message.

## Conversation

**User:**
Hello, how are you?

**Assistant:**
I'm good, thank you! How can I assist you today?

**User (Alice):**
Could you help me with my project?

**Assistant (Bot):**
Absolutely! What do you need help with?
"""

    expected_prompt = StructuredPrompt(
        name="Test Prompt",
        system_message=(
            "This is a test system message.\n"
            "This is a second line of the system message."
        ),
        conversation=[
            Message(role="User", content="Hello, how are you?"),
            Message(
                role="Assistant",
                content="I'm good, thank you! How can I assist you today?",
            ),
            Message(
                role="User",
                content="Could you help me with my project?",
                name="Alice",
            ),
            Message(
                role="Assistant",
                content="Absolutely! What do you need help with?",
                name="Bot",
            ),
        ],
    )

    actual_prompt = StructuredPrompt.from_promptdown_string(promptdown_string)
    assert actual_prompt == expected_prompt, (
        "Failed to parse simplified conversation format correctly."
    )


def test_from_promptdown_string_name_no_space():
    """
    Test that the parser handles `**Role(Name):**` (missing space) correctly.
    """
    promptdown_string = """
# Test Prompt

## System Message
Sys

## Conversation

**User(Alice):**
Content.
"""
    expected_prompt = StructuredPrompt(
        name="Test Prompt",
        system_message="Sys",
        conversation=[
            Message(role="User", content="Content.", name="Alice"),
        ],
    )
    actual_prompt = StructuredPrompt.from_promptdown_string(promptdown_string)
    assert actual_prompt == expected_prompt
