from __future__ import annotations
import logging
from dataclasses import dataclass
from importlib import resources

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
    conversation: list[Message]

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
    def _parse_conversation(cls, lines: list[str]) -> list[Message]:
        """
        Parse the conversation part of a promptdown string into a list of Message objects.

        Args:
            lines (list[str]): The lines of the conversation section from a promptdown string.

        Returns:
            list[Message]: A list of Message instances parsed from the given lines.
        """
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

    def apply_template_values(self, template_values: dict[str, str]) -> None:
        """
        Apply template values to the placeholders in the prompt content, replacing them with the specified values.

        Args:
            template_values (dict[str, str]): A dictionary mapping placeholders (without braces) to their replacement values.
        """
        for key, value in template_values.items():
            placeholder = f"{{{{{key}}}}}"  # Define the placeholder once per key

            # Replace placeholders in the system message
            if placeholder in self.system_message:
                self.system_message = self.system_message.replace(placeholder, value)

            # Replace placeholders in each message in the conversation
            for message in self.conversation:
                if placeholder in message.content:
                    message.content = message.content.replace(placeholder, value)
