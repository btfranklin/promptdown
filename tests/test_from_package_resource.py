import pytest
from importlib import resources
from promptdown import StructuredPrompt, Message


def test_from_package_resource_success():
    """Test successful loading of a structured prompt from a package resource."""

    expected_prompt = StructuredPrompt(
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
                content="That error usually occurs when you try to use a variable that hasn't been declared or "
                + "assigned a value. Can you show me the code where you're encountering this error?",
            ),
        ],
    )

    resource_path = resources.files("tests") / "test.prompt.md"
    with resource_path.open("r", encoding="utf-8") as file:
        promptdown_string = file.read()

        prompt = StructuredPrompt.from_promptdown_string(promptdown_string)

        assert prompt is not None
        assert isinstance(prompt, StructuredPrompt)
        assert prompt.name == expected_prompt.name
        assert prompt.system_message == expected_prompt.system_message
        assert prompt.conversation == expected_prompt.conversation


def test_from_package_resource_failure():
    """Test handling of non-existent file to ensure proper error management."""
    with pytest.raises(FileNotFoundError):
        StructuredPrompt.from_package_resource("tests", "non_existent.prompt.md")
