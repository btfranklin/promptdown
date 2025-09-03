from promptdown import StructuredPrompt, Message
from pathlib import Path


def test_non_ascii_roundtrip(tmp_path: Path):
    filename: Path = tmp_path / "non_ascii.prompt.md"

    prompt = StructuredPrompt(
        name="Überprüfung",
        system_message="Café — naïve façade. 中文，日本語, 한국어.",
        conversation=[
            Message(role="User", content="¿Puedes ayudarme?"),
            Message(role="Assistant", content="Sí, por supuesto."),
        ],
    )

    prompt.to_promptdown_file(str(filename))
    loaded = StructuredPrompt.from_promptdown_file(str(filename))

    assert loaded.name == prompt.name
    assert loaded.system_message == prompt.system_message
    assert loaded.conversation == prompt.conversation
