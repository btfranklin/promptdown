from dataclasses import dataclass


@dataclass
class Message:
    role: str
    content: str
    name: str | None = None

    def __eq__(self, other: object):
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

    def __eq__(self, other: object):
        if isinstance(other, StructuredPrompt):
            return (
                self.name == other.name
                and self.system_message == other.system_message
                and self.conversation == other.conversation
            )
        return False

    @classmethod
    def parse_conversation(cls, lines: list[str]) -> list[Message]:
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
    def from_promptdown_string(cls, promptdown_string: str):
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

        conversation = cls.parse_conversation(conversation_lines)

        return cls(name=name, system_message=system_message, conversation=conversation)

    @classmethod
    def from_promptdown_file(cls, file_path: str):
        promptdown_string = ""
        with open(file_path, "r") as file:
            promptdown_string = file.read()

        return cls.from_promptdown_string(promptdown_string)
