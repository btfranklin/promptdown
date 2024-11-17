from promptdown import StructuredPrompt, Message


def test_apply_template_values_to_object():

    # Create a structured prompt with placeholders
    structured_prompt = StructuredPrompt(
        name="Test Prompt",
        system_message="You are a helpful expert at {topic}.",
        conversation=[
            Message(role="User", content="What is the capital of {country}?"),
            Message(role="Assistant", content="The capital of {country} is {capital}."),
        ],
    )

    # Define template values to apply
    template_values = {"country": "France", "capital": "Paris", "topic": "geography"}

    # Action: Apply the template values
    structured_prompt.apply_template_values(template_values)

    # Assertions to check if the placeholders are correctly replaced
    assert structured_prompt.system_message == "You are a helpful expert at geography."
    if conversation := structured_prompt.conversation:
        assert conversation[0].content == "What is the capital of France?"
        assert conversation[1].content == "The capital of France is Paris."


def test_apply_template_values_to_string():

    # Create a structured prompt from a string with placeholders
    prompt_string = """
# Test Prompt

## System Message

You are a helpful expert at {topic}.

## Conversation

| Role | Content |
|---|---|
| User | What is the capital of {country}? |
| Assistant | The capital of {country} is {capital}. |
"""
    structured_prompt = StructuredPrompt.from_promptdown_string(prompt_string)

    # Define template values to apply
    template_values = {"country": "France", "capital": "Paris", "topic": "geography"}

    # Action: Apply the template values
    structured_prompt.apply_template_values(template_values)

    # Assertions to check if the placeholders are correctly replaced
    assert structured_prompt.system_message == "You are a helpful expert at geography."
    if conversation := structured_prompt.conversation:
        assert conversation[0].content == "What is the capital of France?"
        assert conversation[1].content == "The capital of France is Paris."


def test_system_message_with_json_example():
    # Create a structured prompt from a string with placeholders
    prompt_string = """
# Create Research Questions Prompt

## System Message

There are numbered questions which will be provided. An unrelated value is {value}.

Example:

```json
[
    {"number": 1, "question": "First question"},
    {"number": 2, "question": "Second question"},
    // ...
]
```

## Conversation

**User:**
This would be the user message
"""

    structured_prompt = StructuredPrompt.from_promptdown_string(prompt_string)

    # Define template values to apply
    template_values = {"value": "example value"}

    # Action: Apply the template values
    structured_prompt.apply_template_values(template_values)
