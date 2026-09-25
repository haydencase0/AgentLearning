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
- Optional command-line interface

## Requirements

- Python 3.12 or newer
- A Google Gemini API key
- `uv` recommended for dependency management

The required Python packages are listed in `pyproject.toml`:

- `langchain`
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
