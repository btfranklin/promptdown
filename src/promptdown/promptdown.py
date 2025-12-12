from __future__ import annotations
import logging
import re
from dataclasses import dataclass
from importlib import resources
from typing import Any, cast
from .types import ResponsesMessage, ResponsesPart, Role

_LOGGER = logging.getLogger(__name__)


@dataclass
class Message:
    role: str
    content: str
    name: str | None = None

    def __post_init__(self):
        """
        Validate the role to ensure that it does not use reserved roles ("System" or "Developer").
        Raises:
            ValueError: If the role is a reserved role that cannot be used for conversation messages.
        """
        reserved_roles = {"system", "developer"}
        if self.role.lower() in reserved_roles:
            raise ValueError(
                f"The role '{self.role}' is reserved and cannot be used for conversation messages."
            )


@dataclass
class StructuredPrompt:
    name: str
    system_message: str | None = None
    developer_message: str | None = None
    conversation: list[Message] | None = None

    def __post_init__(self):
        """
        Validate that only one of system_message or developer_message is set.
        Raises:
            ValueError: If both or neither system_message and developer_message are set.
        """
        if (self.system_message is None) == (self.developer_message is None):
            raise ValueError(
                "Exactly one of system_message or developer_message must be set."
            )

    @classmethod
    def _parse_conversation(cls, lines: list[str]) -> list[Message]:
        """
        Parse the conversation part of a promptdown string into a list of Message objects.

        Args:
            lines (list[str]): The lines of the conversation section from a promptdown string.

        Returns:
            list[Message]: A list of Message instances parsed from the given lines.
        """
        conversation: list[Message] = []
        known_roles = {"User", "Assistant"}
        role: str | None = None
        name: str | None = None
        content: list[str] = []

        # Regex to match **Role:** or **Role (Name):**
        # Group 1: Role
        # Group 2: Name (optional)
        role_pattern = re.compile(r"^\*\*([a-zA-Z0-9_ ]+)(?:\s*\(([^)]+)\))?:\*\*$")

        for line in lines:
            # Strip leading/trailing whitespace from the current line
            line_strip = line.strip()

            # Check if the line matches the role pattern
            match = role_pattern.match(line_strip)
            if match:
                # If a role is already set and there is accumulated content,
                # add the message to the conversation list
                if role and content:
                    conversation.append(
                        Message(
                            role=role, content=" ".join(content).strip(), name=name
                        )
                    )
                    content = []
                elif content:
                    # If there's content but no role, it's orphaned content.
                    # We log a warning and discard it.
                    _LOGGER.warning(
                        "Orphaned content found before any role definition. Ignoring."
                    )
                    content = []

                # Extract role and name from the regex match
                found_role = match.group(1).strip()
                found_name = match.group(2).strip() if match.group(2) else None

                # Verify if it is a known role
                if found_role in known_roles:
                    role = found_role
                    name = found_name
                else:
                    _LOGGER.warning(
                        f"Unknown role '{found_role}' encountered in conversation."
                    )
                    role = None
                    name = None
            else:
                # Fallback: Check if it looks like a role but failed regex (e.g. "**:**")
                if line_strip.startswith("**") and line_strip.endswith(":**"):
                    _LOGGER.warning(
                        f"Potential malformed role line encountered: '{line_strip}'"
                    )

                # If it's not a role indicator, consider it part of the message content
                content.append(line)

        # If there is a role set and accumulated content after the last line,
        # append the last message to the conversation
        if role and content:
            conversation.append(
                Message(role=role, content=" ".join(content).strip(), name=name)
            )

        # Return the list of parsed messages
        return conversation

    @classmethod
    def from_promptdown_string(cls, promptdown_string: str) -> StructuredPrompt:
        """
        Parse a structured prompt from a raw promptdown string.

        Args:
            promptdown_string (str): The complete promptdown formatted string to parse.

        Returns:
            StructuredPrompt: A new instance of StructuredPrompt based on the parsed string.

        Raises:
            ValueError: If the promptdown string does not contain necessary sections.
        """
        name: str | None = None
        current_section: str | None = None
        system_message: str | None = None
        developer_message: str | None = None
        system_message_lines: list[str] = []
        developer_message_lines: list[str] = []
        conversation: list[Message] | None = []
        conversation_lines: list[str] = []

        lines = promptdown_string.split("\n")
        for line in lines:
            stripped_line = line.strip()

            if stripped_line.startswith(
                "# "
            ):  # Found the prompt name section, e.g., "# My Prompt"
                name = stripped_line[2:].strip()
                current_section = None
            elif stripped_line.startswith(
                "## "
            ):  # Found a section header, e.g., "## Conversation"
                current_section = stripped_line[3:].strip().lower()
            elif (
                current_section == "system message"
            ):  # We are in the system message section, so this is a line of the system message
                if stripped_line:
                    system_message_lines.append(stripped_line)
            elif (
                current_section == "developer message"
            ):  # We are in the developer message section, so this is a line of the developer message
                if stripped_line:
                    developer_message_lines.append(stripped_line)
            elif (
                current_section == "conversation"
            ):  # We are in the conversation section, so this is a line of the conversation
                conversation_lines.append(stripped_line)

        if name is None:
            raise ValueError(
                "No prompt name found in the promptdown string. A prompt name is required."
            )

        if system_message_lines:
            system_message = "\n".join(system_message_lines)
        if developer_message_lines:
            developer_message = "\n".join(developer_message_lines)

        if not system_message_lines and not developer_message_lines:
            raise ValueError(
                "Neither system message nor developer message found in the promptdown string. One is required."
            )
        if system_message_lines and developer_message_lines:
            raise ValueError(
                "Both system message and developer message found in the promptdown string. Only one is allowed."
            )

        if not conversation_lines:
            conversation = None
        else:
            conversation = cls._parse_conversation(conversation_lines)

        return cls(
            name=name,
            system_message=system_message,
            developer_message=developer_message,
            conversation=conversation,
        )

    @classmethod
    def from_promptdown_file(cls, file_path: str) -> StructuredPrompt:
        """
        Load and parse a StructuredPrompt from a file containing promptdown-formatted text.

        Args:
            file_path (str): The file system path to the promptdown file.

        Returns:
            StructuredPrompt: A new instance of StructuredPrompt based on the content of the file.

        Raises:
            FileNotFoundError: If the specified file is not found.
        """
        if not file_path.endswith(".prompt.md"):
            _LOGGER.warning("Promptdown files should end with '.prompt.md'")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                promptdown_string = file.read()
        except FileNotFoundError:
            _LOGGER.error(f"File {file_path} not found.")
            raise

        return cls.from_promptdown_string(promptdown_string)

    @classmethod
    def from_package_resource(
        cls, package: str, resource_name: str
    ) -> StructuredPrompt:
        """
        Load and parse a StructuredPrompt from a resource within a package.

        Args:
            package (str): The name of the package containing the resource.
            resource_name (str): The name of the resource file to load.

        Returns:
            StructuredPrompt: A new instance of StructuredPrompt based on the resource content.

        Raises:
            FileNotFoundError: If the resource is not found within the specified package.
        """
        if not resource_name.endswith(".prompt.md"):
            _LOGGER.warning("Promptdown files should end with '.prompt.md'")

        try:
            resource_path = resources.files(package) / resource_name
            with resource_path.open("r", encoding="utf-8") as file:
                promptdown_string = file.read()
        except FileNotFoundError:
            _LOGGER.error(f"File {resource_name} not found in package {package}.")
            raise

        return cls.from_promptdown_string(promptdown_string)

    def to_promptdown_string(self) -> str:
        """
        Serialize the StructuredPrompt into a promptdown-formatted string.

        Returns:
            str: The serialized promptdown-formatted string of the StructuredPrompt.
        """
        lines: list[str] = []

        lines.append(f"# {self.name}")
        lines.append("")

        if self.system_message is not None:
            lines.append("## System Message")
            lines.append(self.system_message)
            lines.append("")
        elif self.developer_message is not None:
            lines.append("## Developer Message")
            lines.append(self.developer_message)
            lines.append("")

        if self.conversation is not None:
            # Add the conversation
            lines.append("## Conversation")
            lines.append("")

            # Add each message in the conversation
            for message in self.conversation:
                role = message.role
                content = message.content
                name = message.name
                if name:
                    lines.append(f"**{role} ({name}):**")
                else:
                    lines.append(f"**{role}:**")
                lines.append(content)
                lines.append("")

        return "\n".join(lines)

    def to_promptdown_file(self, file_path: str) -> None:
        """
        Write the StructuredPrompt to a file in promptdown format.

        Args:
            file_path (str): The file system path where the promptdown file will be saved.
        """
        # Check if the file path ends with ".prompt.md"
        if not file_path.endswith(".prompt.md"):
            _LOGGER.warning("Promptdown files should end with '.prompt.md'")

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.to_promptdown_string())

    def to_chat_completion_messages(
        self,
    ) -> list[dict[str, str | list[dict[str, Any]]]]:
        """
        Convert the StructuredPrompt's conversation into the structure needed for a chat completion API client.

        Returns:
            list[dict[str, str | list[dict[str, Any]]]]: A list of message dictionaries suitable for a chat completion API client.
        """
        messages: list[dict[str, str | list[dict[str, Any]]]] = []

        # Start with either system or developer message
        if self.system_message is not None:
            messages.append({"role": "system", "content": self.system_message})
        elif self.developer_message is not None:
            messages.append({"role": "developer", "content": self.developer_message})

        # Add the conversation messages
        if self.conversation is not None:
            for message in self.conversation:
                content: list[dict[str, Any]] = [
                    {"type": "text", "text": message.content}
                ]
                msg: dict[str, Any] = {"role": message.role.lower(), "content": content}
                if message.name:
                    msg["name"] = message.name
                messages.append(msg)

        return messages

    def _coerce_to_response_parts(self, value: object) -> list[ResponsesPart]:
        """
        Coerce a message content value into a list of ResponsesPart objects.

        Args:
            value: The message content, which can be a string, a list of parts, or other types.

        Returns:
            list[ResponsesPart]: A list of well-formed ResponsesPart objects.
        """
        # If already a list of parts, pass through valid parts and coerce others
        if isinstance(value, list):
            parts: list[ResponsesPart] = []
            for part in cast(list[Any], value):
                if isinstance(part, dict):
                    part_dict = cast(dict[str, Any], part)
                    if part_dict.get("type") == "input_text" and "text" in part_dict:
                        text_value = part_dict.get("text")
                        parts.append(
                            {
                                "type": "input_text",
                                "text": ("" if text_value is None else str(text_value)),
                            }
                        )
                        continue
                    # Fallback: coerce unknown dict shapes to text
                    parts.append(
                        {"type": "input_text", "text": str(cast(object, part))}
                    )
                else:
                    parts.append(
                        {"type": "input_text", "text": str(cast(object, part))}
                    )
            # Guarantee non-empty parts
            return parts if parts else [{"type": "input_text", "text": ""}]
        # Otherwise coerce to a single input_text part
        return [{"type": "input_text", "text": "" if value is None else str(value)}]

    def to_responses_input(
        self, map_system_to_developer: bool = True
    ) -> list[ResponsesMessage]:
        """Convert the prompt to the OpenAI Responses API input format.

        Args:
            map_system_to_developer (bool): When True, maps a leading "system" role
                to "developer" for consistency with modern role nomenclature.

        Returns:
            list[ResponsesMessage]: Ordered list of messages with content parts
            formatted for the Responses API.
        """

        messages: list[ResponsesMessage] = []

        # Add the leading system/developer message
        head_role = "system" if self.system_message is not None else "developer"
        if map_system_to_developer and head_role == "system":
            head_role = "developer"
        head_text = (
            self.system_message
            if self.system_message is not None
            else self.developer_message
        )
        messages.append(
            {
                "role": cast(Role, head_role),
                "content": self._coerce_to_response_parts(head_text),
            }
        )

        # Add conversation messages in order
        if self.conversation is not None:
            for message in self.conversation:
                role = message.role.lower()
                if map_system_to_developer and role == "system":
                    role = "developer"
                messages.append(
                    {
                        "role": cast(Role, role),
                        "content": self._coerce_to_response_parts(message.content),
                    }
                )

        return messages

    def apply_template_values(self, template_values: dict[str, str]) -> None:
        """
        Apply template values to the placeholders in the prompt content, replacing them with the specified values.
        NOTE: Template values are not applied if the placeholder is within a triple-backtick code block,
        as this is likely a JSON example.

        Args:
            template_values (dict[str, str]): A dictionary mapping placeholders to their replacement values.
        """

        def replace_placeholders(text: str) -> str:
            # Split the text into code and non-code segments
            segments = re.split(r"(```.*?```)", text, flags=re.DOTALL)
            # Process only the non-code segments
            for i, segment in enumerate(segments):
                if not segment.startswith("```"):
                    segments[i] = segment.format(**template_values)
            return "".join(segments)

        # Replace placeholders in the system or developer message
        if self.system_message is not None:
            self.system_message = replace_placeholders(self.system_message)
        elif self.developer_message is not None:
            self.developer_message = replace_placeholders(self.developer_message)

        # Replace placeholders in each message in the conversation
        if self.conversation is not None:
            for message in self.conversation:
                message.content = replace_placeholders(message.content)
