from promptdown import StructuredPrompt, Message


def test_to_promptdown_string_without_names():
    prompt = StructuredPrompt(
        name="Example Prompt",
        system_message="You are a helpful assistant.",
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

    expected_promptdown_string = "\n".join(
        [
            "# Example Prompt",
            "",
            "## System Message",
            "You are a helpful assistant.",
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

    promptdown_string = prompt.to_promptdown_string()
    assert promptdown_string == expected_promptdown_string


def test_to_promptdown_string_with_names():
    prompt = StructuredPrompt(
        name="Example Prompt with Names",
        system_message="You are a helpful assistant.",
        conversation=[
            Message(role="User", content="Hi", name="Alice"),
            Message(role="Assistant", content="Hello", name="Bob"),
        ],
    )

    expected_promptdown_string = """# Example Prompt with Names

## System Message
You are a helpful assistant.

## Conversation

**User (Alice):**
Hi

**Assistant (Bob):**
Hello
"""
    promptdown_string = prompt.to_promptdown_string()
    assert promptdown_string == expected_promptdown_string
