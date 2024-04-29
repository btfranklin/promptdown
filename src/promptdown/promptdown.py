from __future__ import annotations
import logging
from dataclasses import dataclass
import importlib.resources as pkg_resources

_LOGGER = logging.getLogger(__name__)


@dataclass
class Message:
    role: str
    content: str
    name: str | None = None

    def __eq__(self, other: object) -> bool:
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
    conversation: list[Message]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, StructuredPrompt):
            return (
                self.name == other.name
                and self.system_message == other.system_message
                and self.conversation == other.conversation
            )
        return False

    @classmethod
    def _parse_conversation(cls, lines: list[str]) -> list[Message]:
        conversation: list[Message] = []
        headers: list[str] = []

        # Iterate over each line in the input lines
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
    def from_promptdown_string(cls, promptdown_string: str) -> StructuredPrompt:
        name: str | None = None
        system_message: str | None = None
        conversation: list[Message] = []
        current_section: str | None = None
        conversation_lines: list[str] = []

        lines = promptdown_string.split("\n")
        for line in lines:
            line = line.strip()

            if line.startswith("# "):
                name = line[2:].strip()
            elif line.startswith("## "):
                current_section = line[3:].strip().lower()
            elif current_section == "system message" and line:
                system_message = line
            elif current_section == "conversation":
                conversation_lines.append(line)

        if name is None:
            raise ValueError(
                "No prompt name found in the promptdown string. A prompt name is required."
            )
        if system_message is None:
            raise ValueError(
                "No system message found in the promptdown string. A system message is required."
            )

        conversation = cls._parse_conversation(conversation_lines)

        return cls(name=name, system_message=system_message, conversation=conversation)

    @classmethod
    def from_promptdown_file(cls, file_path: str) -> StructuredPrompt:
        """
        Load a promptdown file from a filesystem path.

        Args:
        file_path: The path to the promptdown file.

        Returns:
        A StructuredPrompt object loaded from the specified file.
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
        Load a promptdown file as a structured prompt from a package resource.

        Args:
        package: The package name where the resource is located.
        resource_name: The name of the promptdown resource file.

        Returns:
        A StructuredPrompt object loaded from the specified package resource.
        """
        if not resource_name.endswith(".prompt.md"):
            _LOGGER.warning("Promptdown files should end with '.prompt.md'")

        try:
            with pkg_resources.open_text(package, resource_name) as file:
                promptdown_string = file.read()
        except FileNotFoundError:
            _LOGGER.error(f"File {resource_name} not found in package {package}.")
            raise

        return cls.from_promptdown_string(promptdown_string)

    def to_promptdown_string(self) -> str:
        lines: list[str] = []

        # Add the name of the prompt
        lines.append(f"# {self.name}")
        lines.append("")

        # Add the system message
        lines.append("## System Message")
        lines.append(self.system_message)
        lines.append("")

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

        # Check if the file path ends with ".prompt.md"
        if not file_path.endswith(".prompt.md"):
            _LOGGER.warning("Promptdown files should end with '.prompt.md'")

        with open(file_path, "w") as file:
            file.write(self.to_promptdown_string())
