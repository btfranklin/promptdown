from promptdown import StructuredPrompt, Message


def test_apply_template_values_to_object():

    # Create a structured prompt with placeholders
    structured_prompt = StructuredPrompt(
        name="Test Prompt",
        system_message="You are a helpful expert at {{topic}}.",
        conversation=[
            Message(role="User", content="What is the capital of {{country}}?"),
            Message(
                role="Assistant", content="The capital of {{country}} is {{capital}}."
            ),
        ],
    )

    # Define template values to apply
    template_values = {"country": "France", "capital": "Paris", "topic": "geography"}

    # Action: Apply the template values
    structured_prompt.apply_template_values(template_values)

    # Assertions to check if the placeholders are correctly replaced
    assert structured_prompt.system_message == "You are a helpful expert at geography."
    assert structured_prompt.conversation[0].content == "What is the capital of France?"
    assert (
        structured_prompt.conversation[1].content == "The capital of France is Paris."
    )


def test_apply_template_values_to_string():

    # Create a structured prompt from a string with placeholders
    prompt_string = """
# Test Prompt

## System Message

You are a helpful expert at {{topic}}.

## Conversation

| Role | Content |
|---|---|
| User | What is the capital of {{country}}? |
| Assistant | The capital of {{country}} is {{capital}}. |
"""
    structured_prompt = StructuredPrompt.from_promptdown_string(prompt_string)

    # Define template values to apply
    template_values = {"country": "France", "capital": "Paris", "topic": "geography"}

    # Action: Apply the template values
    structured_prompt.apply_template_values(template_values)

    # Assertions to check if the placeholders are correctly replaced
    assert structured_prompt.system_message == "You are a helpful expert at geography."
    assert structured_prompt.conversation[0].content == "What is the capital of France?"
    assert (
        structured_prompt.conversation[1].content == "The capital of France is Paris."
    )
