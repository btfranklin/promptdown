from promptdown import StructuredPrompt, Message


def test_to_promptdown_string_without_names():
    prompt = StructuredPrompt(
        name="Example Prompt",
        system_message="You are a helpful assistant.",
        conversation=[
            Message(role="User", content="Hi, can you help me?"),
            Message(
                role="Assistant", content="Of course! What do you need assistance with?"
            ),
            Message(role="User", content="I'm having trouble with my code."),
            Message(
                role="Assistant",
                content="I'd be happy to help. What seems to be the problem?",
            ),
            Message(
                role="User",
                content='I\'m getting an error message that says "undefined variable".',
            ),
            Message(
                role="Assistant",
                content="That error usually occurs when you try to use a variable that hasn't been declared "
                + "or assigned a value. Can you show me the code where you're encountering this error?",
            ),
        ],
    )

    expected_promptdown_string = """# Example Prompt

## System Message
You are a helpful assistant.

## Conversation

| Role | Content |
| --- | --- |
| User | Hi, can you help me? |
| Assistant | Of course! What do you need assistance with? |
| User | I'm having trouble with my code. |
| Assistant | I'd be happy to help. What seems to be the problem? |
| User | I'm getting an error message that says "undefined variable". |
| Assistant | That error usually occurs when you try to use a variable that hasn't been declared or assigned a value. Can you show me the code where you're encountering this error? |"""  # noqa: E501

    promptdown_string = prompt.to_promptdown_string()
    assert promptdown_string == expected_promptdown_string


def test_to_promptdown_string_with_names():
    prompt = StructuredPrompt(
        name="Example Prompt",
        system_message="You are a helpful assistant.",
        conversation=[
            Message(role="User", name="Alice", content="Hi, can you help me?"),
            Message(
                role="Assistant",
                name="Bot",
                content="Of course! What do you need assistance with?",
            ),
            Message(
                role="User", name="Alice", content="I'm having trouble with my code."
            ),
            Message(
                role="Assistant",
                name="Bot",
                content="I'd be happy to help. What seems to be the problem?",
            ),
            Message(
                role="User",
                name="Alice",
                content='I\'m getting an error message that says "undefined variable".',
            ),
            Message(
                role="Assistant",
                name="Bot",
                content="That error usually occurs when you try to use a variable that hasn't been declared or assigned a value. Can you show me the code where you're encountering this error?",
            ),
        ],
    )

    expected_promptdown_string = """# Example Prompt

## System Message
You are a helpful assistant.

## Conversation

| Role | Name | Content |
| --- | --- | --- |
| User | Alice | Hi, can you help me? |
| Assistant | Bot | Of course! What do you need assistance with? |
| User | Alice | I'm having trouble with my code. |
| Assistant | Bot | I'd be happy to help. What seems to be the problem? |
| User | Alice | I'm getting an error message that says "undefined variable". |
| Assistant | Bot | That error usually occurs when you try to use a variable that hasn't been declared or assigned a value. Can you show me the code where you're encountering this error? |"""  # noqa: E501

    promptdown_string = prompt.to_promptdown_string()
    assert promptdown_string == expected_promptdown_string
