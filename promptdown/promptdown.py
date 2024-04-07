from dataclasses import dataclass


@dataclass
class Message:
    role: str
    content: str
    name: str | None = None


@dataclass
class StructuredPrompt:
    name: str
    system_message: str
    conversation: list[Message]

    @classmethod
    def from_promptdown_string(cls, promptdown_string: str):
        name: str | None = None
        system_message: str | None = None
        conversation: list[Message] = []
        current_section: str | None = None

        lines = promptdown_string.split("\n")
        for line in lines:
            line = line.strip()

            if line.startswith("# "):
                name = line[2:].strip()
            elif line.startswith("## "):
                current_section = line[3:].strip().lower()
            elif current_section == "system message" and line:
                system_message = line
            elif current_section == "conversation" and line.startswith("|"):
                parts = [part.strip() for part in line.split("|") if part.strip()]
                if len(parts) == 2:
                    role, content = parts
                    conversation.append(Message(role=role.lower(), content=content))

        if name is None:
            raise ValueError(
                "No prompt name found in the promptdown string. A prompt name is required."
            )
        if system_message is None:
            raise ValueError(
                "No system message found in the promptdown string. A system message is required."
            )

        return cls(name=name, system_message=system_message, conversation=conversation)

    @classmethod
    def from_promptdown_file(cls, file_path: str):
        promptdown_string = ""
        with open(file_path, "r") as file:
            promptdown_string = file.read()

        return cls.from_promptdown_string(promptdown_string)
