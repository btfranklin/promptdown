import pytest
from promptdown import StructuredPrompt

def test_missing_name():
    prompt_string = """
## System Message

You are a helpful assistant.
"""
    with pytest.raises(ValueError, match="No prompt name found"):
        StructuredPrompt.from_promptdown_string(prompt_string)

def test_missing_system_and_developer_message():
    prompt_string = """
# My Prompt

## Conversation

**User:**
Hi.
"""
    with pytest.raises(ValueError, match="Neither system message nor developer message found"):
        StructuredPrompt.from_promptdown_string(prompt_string)

def test_both_system_and_developer_message():
    prompt_string = """
# My Prompt

## System Message
System

## Developer Message
Developer
"""
    with pytest.raises(ValueError, match="Both system message and developer message found"):
        StructuredPrompt.from_promptdown_string(prompt_string)

def test_unknown_role_warning(caplog):
    prompt_string = """
# My Prompt

## System Message
System

## Conversation

**UnknownRole:**
Content
"""
    StructuredPrompt.from_promptdown_string(prompt_string)
    assert "Unknown role 'UnknownRole' encountered" in caplog.text

def test_malformed_conversation_no_role(caplog):
    """
    Test that content appearing before any role definition is effectively ignored.
    """
    prompt_string = """
# My Prompt

## System Message
System

## Conversation

Orphaned content line.

**User:**
Real content.
"""
    prompt = StructuredPrompt.from_promptdown_string(prompt_string)
    assert len(prompt.conversation) == 1
    assert prompt.conversation[0].content == "Real content."
    assert "Orphaned content found before any role definition. Ignoring." in caplog.text

def test_empty_role_declaration(caplog):
    """
    Test behavior when **Role:** is present but empty or malformed.
    """
    prompt_string = """
# My Prompt

## System Message
System

## Conversation

**:**
"""
    # This parses as a role line but extracts empty string as role.
    # The code checks `if role in known_roles`. "" is not in known_roles.
    # So it should warn "Unknown role '' encountered".
    prompt = StructuredPrompt.from_promptdown_string(prompt_string)
    assert prompt.conversation == []
    assert "Potential malformed role line encountered: '**:**'" in caplog.text

def test_orphaned_whitespace_ignored(caplog):
    """
    Test that whitespace appearing before any role definition is silently ignored
    and does NOT trigger a warning.
    """
    prompt_string = """
# My Prompt

## System Message
System

## Conversation

  

**User:**
Content
"""
    # clear any previous logs
    caplog.clear()
    
    prompt = StructuredPrompt.from_promptdown_string(prompt_string)
    
    # We expect NO warning about orphaned content because it's just whitespace
    assert "Orphaned content found before any role definition. Ignoring." not in caplog.text
    
    # Verify the conversation matches parsed correctly
    assert len(prompt.conversation) == 1
    assert prompt.conversation[0].role == "User"
    assert prompt.conversation[0].content == "Content"
