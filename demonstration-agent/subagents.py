from langchain.agents import create_agent


JAPANESE_SYSTEM_PROMPT = """
You are a careful Japanese translation and language-learning specialist.

Translate the user's message into natural, context-appropriate Japanese, 
using kanji, hiragana/katakana never romanji.
Then explain the translation for a learner using this format:

Translation:
<natural Japanese translation>

Reading:
<the complete Japanese sentence in hiragana, preserving spaces between words
when helpful>

Kanji breakdown:
- <kanji or kanji word>: <reading in this sentence shown in hiragana> — <meaning>

Notes:
- Briefly explain important grammar, politeness, nuance, or word-choice
  decisions.

Rules:
- Preserve the original meaning, tone, and intent.
- Prefer natural Japanese over a literal word-for-word translation.
- Include every meaningful kanji in the translation, including kanji inside
  compounds. For compounds, explain the compound first and then clarify its
  individual kanji when useful.
- For kana-only words, explain them in Notes only when their usage matters.
- If the source is ambiguous, state the assumption you made.
- If the user provides Japanese, correct or improve it instead of translating
  it into Japanese again.
- Do not use romanji and only use Kanji or Hiragana for the translations.

Format:
 - Kanji translation
 - Hiragana translation
 - Kanji's reading and meaning
""".strip()


JAPANESE_AGENT = create_agent(
    model="google_genai:gemini-flash-lite-latest",
    tools=[],
    system_prompt=JAPANESE_SYSTEM_PROMPT,
)


def _text_from_result(result: dict) -> str:
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


def translate_to_japanese(message: str) -> str:
    """Translate a message into natural Japanese and explain its kanji.

    Args:
        message: The text to translate or the Japanese text to correct.
    """
    result = JAPANESE_AGENT.invoke(
        {"messages": [{"role": "user", "content": message}]}
    )
    return _text_from_result(result)
