from __future__ import annotations
import logging
import re
from dataclasses import dataclass
from importlib import resources
from typing import Any

_LOGGER = logging.getLogger(__name__)


@dataclass
class Message:
    role: str
    content: str
    name: str | None = None

    def __post_init__(self):
        """
        Validate the role to ensure that it does not use the reserved role "System".
        Raises:
            ValueError: If the role is set to "System", which is reserved.
        """
        if self.role.lower() == "system":
            raise ValueError(
                "The role 'System' is reserved and cannot be used for conversation messages."
            )

    def __eq__(self, other: object) -> bool:
        """
        Check equality between two Message instances based on role, content, and name.

        Args:
            other (object): The other object to compare with.

        Returns:
            bool: True if both objects are Messages and have the same role, content, and name; False otherwise.
        """
        if isinstance(other, Message):
            return (
                self.role.lower() == other.role.lower()
                and self.content == other.content
                and self.name == other.name
            )
        return False


@dataclass
class StructuredPrompt:
    name: str
    system_message: str
    conversation: list[Message] | None = None

    def __eq__(self, other: object) -> bool:
        """
        Check equality between two StructuredPrompt instances based on name, system_message, and conversation.

        Args:
            other (object): The other object to compare with.

        Returns:
            bool: True if both are StructuredPrompts with the same name, system_message, and conversation; False otherwise.
        """
        if isinstance(other, StructuredPrompt):
            return (
                self.name == other.name
                and self.system_message == other.system_message
                and self.conversation == other.conversation
            )
        return False

    @classmethod
    def _parse_conversation_table(cls, lines: list[str]) -> list[Message]:
        """
        Parse the conversation from the given list of lines using the table-based format.

        This method assumes that the conversation section follows a table structure,
        where each row represents a message with columns like Role, Name (optional),
        and Content.

        Args:
            lines (list[str]): A list of lines containing the conversation section.

        Returns:
            list[Message]: A list of Message objects representing the parsed conversation.
        """
        conversation: list[Message] = []
        headers: list[str] = []

        for line in lines:
            # Check if the line starts with "|", indicating a conversation row
            if line.startswith("|"):
                # Split the line by "|" and remove leading/trailing whitespace from each part
                parts = [part.strip() for part in line.split("|") if part.strip()]

                # If headers list is empty, it means we are parsing the first row which contains the headers
                if not headers:
                    headers = parts
                else:
                    # Skip the divider line (e.g., "|---|---|---|")
                    if all(part == "-" * len(part) for part in parts):
                        continue

                    # Create a dictionary to store the message data
                    message_data: dict[str, str] = {
                        header.lower(): "" for header in headers
                    }

                    # Iterate over the headers and corresponding parts, and update the message data dictionary
                    for header, value in zip(headers, parts):
                        message_data[header.lower()] = value

                    # Create a new Message object using the message data and append it to the conversation list
                    conversation.append(
                        Message(
                            role=message_data.get("role", "user"),
                            content=message_data.get("content", ""),
                            name=message_data.get("name"),
                        )
                    )

        # Return the parsed conversation list
        return conversation

    @classmethod
    def _parse_conversation_simplified(cls, lines: list[str]) -> list[Message]:
        """
        Parse the conversation from the given list of lines using the simplified format.

        In this format, each message is identified by the role specified with double asterisks
        (**Role:**) at the beginning of the message. Each subsequent line without a new role
        will be considered part of the message's content until the next role line is encountered.

        Args:
            lines (list[str]): A list of lines containing the conversation section.

        Returns:
            list[Message]: A list of Message objects representing the parsed conversation.
        """
        conversation: list[Message] = []
        known_roles = {"User", "Assistant"}
        role: str | None = None
        content: list[str] = []

        for line in lines:
            # Strip leading/trailing whitespace from the current line
            line_strip = line.strip()

            # If the line starts and ends with double asterisks, it's a role indicator
            if line_strip.startswith("**") and line_strip.endswith(":**"):
                # If a role is already set and there is accumulated content,
                # add the message to the conversation list
                if role and content:
                    conversation.append(
                        Message(role=role, content=" ".join(content).strip())
                    )
                    # Clear content to start collecting the next message
                    content = []

                # Extract the role name from the asterisks and colon, e.g., "**User:**"
                role_line = line_strip.strip("*")
                role, _, _ = role_line.partition(":")

                # If the role is one of the known roles, update the role variable
                if role in known_roles:
                    role = role.strip()
                else:
                    _LOGGER.warning(
                        f"Unknown role '{role}' encountered in conversation."
                    )
                    role = None
            else:
                # If it's not a role indicator, consider it part of the message content
                content.append(line)

        # If there is a role set and accumulated content after the last line,
        # append the last message to the conversation
        if role and content:
            conversation.append(Message(role=role, content=" ".join(content).strip()))

        # Return the list of parsed messages
        return conversation

    @classmethod
    def _parse_conversation(cls, lines: list[str]) -> list[Message]:
        """
        Parse the conversation part of a promptdown string into a list of Message objects.

        Args:
            lines (list[str]): The lines of the conversation section from a promptdown string.

        Returns:
            list[Message]: A list of Message instances parsed from the given lines.
        """
        # Skip empty lines until finding a non-whitespace character
        for line in lines:
            stripped_line = line.strip()

            # If we find a line with non-whitespace content, check its first character
            if stripped_line:
                # If the first non-whitespace character is a pipe, it's a table format
                if stripped_line[0] == "|":
                    return cls._parse_conversation_table(lines)
                # Otherwise, assume the simplified format
                return cls._parse_conversation_simplified(lines)

        # If no content is found, return an empty list
        return []

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
        system_message_lines: list[str] = []
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
                current_section == "conversation"
            ):  # We are in the conversation section, so this is a line of the conversation
                conversation_lines.append(stripped_line)

        if name is None:
            raise ValueError(
                "No prompt name found in the promptdown string. A prompt name is required."
            )

        if not system_message_lines:
            raise ValueError(
                "No system message found in the promptdown string. A system message is required."
            )

        system_message = "\n".join(system_message_lines)

        if not conversation_lines:
            conversation = None
        else:
            conversation = cls._parse_conversation(conversation_lines)

        return cls(name=name, system_message=system_message, conversation=conversation)

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
            with open(file_path, "r") as file:
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

        # Add the name of the prompt
        lines.append(f"# {self.name}")
        lines.append("")

        # Add the system message
        lines.append("## System Message")
        lines.append(self.system_message)
        lines.append("")

        if self.conversation is not None:
            # Add the conversation
            lines.append("## Conversation")
            lines.append("")

            # Check if any message has a name set
            include_name_column = any(message.name for message in self.conversation)

            # Add the table headers
            headers = ["Role"]
            if include_name_column:
                headers.append("Name")
            headers.append("Content")
            lines.append(f"| {' | '.join(headers)} |")
            lines.append(f"| {' | '.join(['---'] * len(headers))} |")

            # Add each message in the conversation
            for message in self.conversation:
                role = message.role
                content = message.content
                if include_name_column:
                    name = message.name if message.name is not None else ""
                    lines.append(f"| {role} | {name} | {content} |")
                else:
                    lines.append(f"| {role} | {content} |")

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

        with open(file_path, "w") as file:
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

        # Start with the system message
        messages.append({"role": "system", "content": self.system_message})

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

        # Replace placeholders in the system message
        self.system_message = replace_placeholders(self.system_message)

        # Replace placeholders in each message in the conversation
        if self.conversation is not None:
            for message in self.conversation:
                message.content = replace_placeholders(message.content)
