from promptdown import StructuredPrompt


def test_only_single_line_developer_message_from_promptdown_string():
    promptdown_string = """
# Example Prompt

## Developer Message

You are a helpful assistant. You are an expert in Python programming.
"""

    expected_prompt = StructuredPrompt(
        name="Example Prompt",
        developer_message="You are a helpful assistant. You are an expert in Python programming.",
    )

    prompt = StructuredPrompt.from_promptdown_string(promptdown_string)
    assert prompt is not None
    assert isinstance(prompt, StructuredPrompt)
    assert prompt.name == expected_prompt.name
    assert prompt.developer_message == expected_prompt.developer_message
    assert prompt.conversation == expected_prompt.conversation


def test_only_multi_line_developer_message_from_promptdown_string():
    promptdown_string = """
# Example Prompt

## Developer Message

You are a helpful assistant. You are an expert in Python programming.

When you are answering a question, you should try focus on using best practices and good coding style.
"""

    expected_prompt = StructuredPrompt(
        name="Example Prompt",
        developer_message="You are a helpful assistant. You are an expert in Python programming.\nWhen you are answering a question, you should try focus on using best practices and good coding style.",
    )

    prompt = StructuredPrompt.from_promptdown_string(promptdown_string)
    assert prompt is not None
    assert isinstance(prompt, StructuredPrompt)
    assert prompt.name == expected_prompt.name
    assert prompt.developer_message == expected_prompt.developer_message
    assert prompt.conversation == expected_prompt.conversation


def test_only_developer_message_to_promptdown_string():
    prompt = StructuredPrompt(
        name="Example Prompt",
        developer_message="You are a helpful assistant. You are an expert in Python programming.\n\nWhen you are answering a question, you should try focus on using best practices and good coding style.",
    )

    expected_promptdown_string = """# Example Prompt

## Developer Message
You are a helpful assistant. You are an expert in Python programming.

When you are answering a question, you should try focus on using best practices and good coding style.
"""

    promptdown_string = prompt.to_promptdown_string()
    assert promptdown_string == expected_promptdown_string
