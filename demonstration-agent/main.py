import argparse
import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langgraph.checkpoint.memory import InMemorySaver
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

if not os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from gui import run_gui
from subagents import translate_to_japanese
from tools import list_directory, read_personal_files, read_safe_file

import logging
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("langchain_google_genai._function_utils").setLevel(logging.ERROR)
logging.disable(logging.WARNING)

import warnings
from langchain_core._api import LangChainBetaWarning
warnings.filterwarnings("ignore", category=LangChainBetaWarning)


console = Console()

# Keep these objects alive and reuse the same thread so the agent can retain
# conversation history for the lifetime of the application.
CHECKPOINTER = InMemorySaver()
THREAD_CONFIG = {"configurable": {"thread_id": "main-chat"}}

MCP_CONFIG = {
    "mcpServers": {
        "arxiv": {
            "command": "uvx",
            "args": ["arxiv-mcp-server"],
        },
        "langchain_docs": {
            "url": "https://docs.langchain.com/mcp",
        },
    }
}

SYSTEM_PROMPT = (
    "You are a helpful assistant who is a mega nerd. Every "
    "sentence you say has to be stated as a matter of fact. "
    "End each sentence like an anime character, using sounds such as "
    "'nano', 'desu', or 'noja'. You roleplay as an anime main character. "
    "Use the available tools when they can provide accurate information."
    " Use translate_to_japanese when the user asks for Japanese translation, "
    "Japanese corrections, kanji readings, or kanji explanations."
)


def _get_text_response(result: dict) -> str:
    """Extract only the final assistant text from an agent result."""
    content = result["messages"][-1].content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") if isinstance(block, dict)
            else getattr(block, "text", "")
            for block in content
        )
    return str(content)


async def _get_response(prompt: str) -> str:
    """Connect to MCP servers, invoke the agent, and return its response."""
    async with MCPAdapter(MCP_CONFIG) as adapter:
        mcp_tools = await adapter.list_tools()
        agent = create_agent(
            model="google_genai:gemini-flash-lite-latest",
            tools=[
                read_safe_file,
                list_directory,
                read_personal_files,
                translate_to_japanese,
                *mcp_tools,
            ],
            checkpointer=CHECKPOINTER,
            system_prompt=SYSTEM_PROMPT,
        )
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            THREAD_CONFIG,
        )
        return _get_text_response(result)


def get_response(prompt: str) -> str:
    """Synchronous wrapper used by both the GUI and CLI."""
    return asyncio.run(_get_response(prompt))


def run_cli() -> None:
    while True:
        print("\n-------- User ---------")
        try:
            prompt = input("Input: ")
            if prompt == "exit":
                break
            response = get_response(prompt)
        except EOFError:
            break
        print("\n--------- AI ----------")
        console.print(Markdown(response))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the agent interaction tool.")
    parser.add_argument(
        "--cli", action="store_true", help="Use the command-line interface."
    )
    args = parser.parse_args()
    run_cli() if args.cli else run_gui(get_response)


if __name__ == "__main__":
    main()
