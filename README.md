# Promptdown

Promptdown is a Python package that allows you to express structured prompts for language models in a markdown format. It provides a simple and intuitive way to define and manage prompts, making it easier to work with language models in your projects.

## Installation

### Using PDM

Promptdown can be installed using PDM:

```bash
pdm add promptdown
```

### Using pip

Alternatively, you can install Promptdown using pip:

```bash
pip install promptdown
```

## Usage

### Basic Usage

To use Promptdown, simply create a Promptdown file (`.prompt.md`) with the following format:

```markdown
# My Prompt

## System Message

You are a helpful assistant.

## Conversation

| Role      | Content                                     |
|-----------|---------------------------------------------|
| User      | Hi, can you help me?                        |
| Assistant | Of course! What do you need assistance with?|
| User      | I'm having trouble with my code.            |
| Assistant | I'd be happy to help. What seems to be the problem? |
```

Then, you can parse this file into a `StructuredPrompt` object using Promptdown:

```python
from promptdown import StructuredPrompt

structured_prompt = StructuredPrompt.from_promptdown_file('path/to/your_prompt_file.prompt.md')
print(structured_prompt)
```

### Advanced Usage

Promptdown provides several methods for loading and utilizing structured prompts beyond the basic file usage. Here are more advanced ways to integrate Promptdown into your projects:

#### Parsing a Prompt from a String

For scenarios where you have the prompt data as a string (perhaps dynamically generated or retrieved from an external source), you can parse it directly:

```python
from promptdown import StructuredPrompt

promptdown_string = """
# My Prompt

## System Message

You are a helpful assistant.

## Conversation

| Role      | Content                                     |
|-----------|---------------------------------------------|
| User      | Hi, can you help me?                        |
| Assistant | Of course! What do you need assistance with?|
| User      | I'm having trouble with my code.            |
| Assistant | I'd be happy to help. What seems to be the problem? |
"""

structured_prompt = StructuredPrompt.from_promptdown_string(promptdown_string)
print(structured_prompt)
```

#### Loading Prompts from Package Resources

For applications where prompts are bundled within Python packages, Promptdown can load prompts directly from these resources. This approach is useful for distributing prompts alongside Python libraries or applications:

```python
from promptdown import StructuredPrompt

structured_prompt = StructuredPrompt.from_package_resource('your_package', 'your_prompt_file.prompt.md')
print(structured_prompt)
```

This method facilitates easy management of prompts within a package, ensuring that they can be versioned, shared, and reused effectively.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

Promptdown is released under the [MIT License](LICENSE).
