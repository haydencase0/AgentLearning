# Demonstration Agent

A small Python agent interface built with Tkinter, LangChain, and Google Gemini.
The default interface is a desktop chat window with user messages aligned to the
right and agent responses aligned to the left.

## Features

- Tkinter chat-style graphical interface
- Multi-line message input
- Send messages with the return-arrow button or Enter
- Use Shift+Enter to add a new line
- Scrollable conversation history
- Gemini responses through LangChain
- Local file tools and personal context files
- ArXiv and LangChain documentation MCP tools
- Japanese translation subagent with kanji explanations
- Optional command-line interface

## Requirements

- Python 3.12 or newer
- A Google Gemini API key
- `uv` recommended for dependency management

The required Python packages are listed in `pyproject.toml`:

- `langchain`
- `langchain[mcp]`
- `langchain-google-genai`
- `python-dotenv`

Tkinter is included with most standard Windows Python installations. On Linux,
install your distribution's Tkinter package if it is not already available.

## Setup

From this directory, create or update the virtual environment:

```powershell
uv sync
```

Create a file named `.env` in this directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Do not commit the `.env` file. It is already excluded by `.gitignore`.

## Personal files

Create a `personal_files/` folder beside `main.py` for information you want
the agent to be able to reference:

```text
demonstration-agent/
└── personal_files/
    ├── profile.md
    ├── preferences.txt
    └── projects.md
```

The `read_personal_files` tool reads supported text files from this folder:

- `.md`
- `.txt`
- `.json`
- `.yaml` and `.yml`
- `.csv`

Ask the agent something like:

```text
What do you know about my projects?
```

The main agent can call `read_personal_files` to load the folder contents. The
tool does not accept an arbitrary path, so it cannot use this feature to read
files outside `personal_files/`. The folder is excluded by `.gitignore`; keep
private information there and do not commit it.

Personal files are persistent local context, not conversation memory. The
agent's conversation memory currently uses an in-memory checkpointer and is
cleared when the application closes.

## Tools and agents

The project has one main agent, local tools, MCP tools, and a Japanese
subagent.

### Local tools

The tools in `tools.py` are registered with the main agent:

- `read_safe_file(path)` reads a UTF-8 file inside the project directory.
- `list_directory(path)` lists files and folders inside the project directory.
- `read_personal_files()` reads supported files from `personal_files/`.

The local tools restrict paths to the project directory and block sensitive
`.env` paths.

### MCP tools

The main agent connects to the MCP servers configured in `main.py`:

- The ArXiv server is launched with `uvx arxiv-mcp-server`.
- The LangChain documentation server is accessed at
  `https://docs.langchain.com/mcp`.

For example, you can ask:

```text
Find recent papers about AI agents on ArXiv.
```

or:

```text
How do I add short-term memory to a LangChain agent?
```

The ArXiv server requires `uvx` to be installed and may download its package
the first time it is used.

### Japanese subagent

The Japanese subagent is defined in `subagents.py` and exposed to the main
agent as the `translate_to_japanese` tool. It can:

- Translate English or other text into natural Japanese
- Provide a complete hiragana reading
- Explain each meaningful kanji and its contextual reading
- Explain grammar, politeness, nuance, and word choices
- Correct Japanese text that is already written in Japanese

Try prompts such as:

```text
Translate "I am learning Python" into Japanese and explain every kanji.
```

```text
Translate this politely into Japanese: "Could you help me?"
```

```text
Correct this Japanese sentence and explain each kanji:
私は日本語を勉強しますた。
```

The main agent decides when to call the subagent. The subagent has its own
system prompt and does not have access to the file or MCP tools.

## Run the GUI

```powershell
uv run python main.py
```

Alternatively, run it directly using the virtual environment:

```powershell
.venv\Scripts\python.exe main.py
```

## Run the command-line interface

```powershell
uv run python main.py --cli
```

Enter prompts at the terminal. Type `exit` to quit.

## Configuration

The Gemini model is configured in `main.py`:

```python
model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key,
    temperature=0,
)
```

Change the `model` value if you want to use another Gemini model available to
your API key.

## Troubleshooting

### `ModuleNotFoundError: No module named 'dotenv'`

Install dependencies into the project's environment:

```powershell
uv sync
```

Make sure your editor is using:

```text
demonstration-agent\.venv\Scripts\python.exe
```

The package is installed as `python-dotenv`, but imported in Python as:

```python
from dotenv import load_dotenv
```

### `GEMINI_API_KEY is missing`

Confirm that `.env` is located beside `main.py` and contains the variable in
this format:

```env
GEMINI_API_KEY=your_api_key_here
```

Never put the key directly into source code or commit it to version control.

## Project structure

```text
demonstration-agent/
├── main.py             # GUI, CLI, and agent integration
├── .env                # Local API key; do not commit
├── pyproject.toml      # Project metadata and dependencies
├── uv.lock             # Locked dependency versions
└── src/ds295r/         # Package source
```
