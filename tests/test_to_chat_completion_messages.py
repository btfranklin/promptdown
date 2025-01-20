from promptdown import StructuredPrompt, Message


def test_to_chat_completion_messages_without_names():
    prompt = StructuredPrompt(
        name="Example Prompt",
        system_message="You are a helpful assistant.\n\nYou should try to provide clear and concise answers to the user's questions.",
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

    expected_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant.\n\nYou should try to provide clear and concise answers to the user's questions.",
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": "Hi, can you help me?"}],
        },
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Of course! What do you need assistance with?"}
            ],
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": "I'm having trouble with my code."}],
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "I'd be happy to help. What seems to be the problem?",
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": 'I\'m getting an error message that says "undefined variable".',
                }
            ],
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "That error usually occurs when you try to use a variable that hasn't been declared or assigned a value. Can you show me the code where you're encountering this error?",
                }
            ],
        },
    ]

    messages = prompt.to_chat_completion_messages()
    assert messages == expected_messages


def test_to_chat_completion_messages_with_names():
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

    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hi, can you help me?",
                }
            ],
            "name": "Alice",
        },
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Of course! What do you need assistance with?"}
            ],
            "name": "Bot",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "I'm having trouble with my code.",
                }
            ],
            "name": "Alice",
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "I'd be happy to help. What seems to be the problem?",
                }
            ],
            "name": "Bot",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": 'I\'m getting an error message that says "undefined variable".',
                }
            ],
            "name": "Alice",
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "That error usually occurs when you try to use a variable that hasn't been declared or assigned a value. Can you show me the code where you're encountering this error?",
                }
            ],
            "name": "Bot",
        },
    ]

    messages = prompt.to_chat_completion_messages()
    assert messages == expected_messages


def test_to_chat_completion_messages_with_developer_message():
    prompt = StructuredPrompt(
        name="Example Prompt",
        developer_message="You are a helpful assistant.\n\nYou should try to provide clear and concise answers to the user's questions.",
        conversation=[
            Message(role="User", content="Hi, can you help me?"),
            Message(
                role="Assistant", content="Of course! What do you need assistance with?"
            ),
        ],
    )

    expected_messages = [
        {
            "role": "developer",
            "content": "You are a helpful assistant.\n\nYou should try to provide clear and concise answers to the user's questions.",
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": "Hi, can you help me?"}],
        },
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Of course! What do you need assistance with?"}
            ],
        },
    ]

    messages = prompt.to_chat_completion_messages()
    assert messages == expected_messages
