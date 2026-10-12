"""
LLM commit message generator using Google Gemini.
"""

import re
from typing import Optional, Tuple
import google.generativeai as genai

MAX_DIFF_CHARS = 24000


def clean_commit_message(raw_text: str) -> str:
    """Clean markdown formatting and fences from model response."""
    text = raw_text.strip()
    
    # Remove markdown code block fences if present
    fence_pattern = r"^```(?:git|markdown|commit|text)?\n([\s\S]*?)\n```$"
    match = re.match(fence_pattern, text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    elif text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2:
            text = "\n".join(lines[1:-1]).strip()

    # Remove quotes wrapping entire message
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()

    return text


def generate_commit_message(
    diff: str,
    api_key: str,
    model_name: str = "gemini-2.5-flash",
    hint: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate conventional commit message from git diff using Gemini.
    Returns (commit_message, error_message).
    """
    if not diff or not diff.strip():
        return None, "No staged changes detected to generate a commit message."

    try:
        genai.configure(api_key=api_key)
        
        # Ensure model name format
        target_model = model_name
        if not target_model.startswith("models/") and not target_model.startswith("gemini-"):
            target_model = f"models/{target_model}"

        model = genai.GenerativeModel(target_model)

        # Truncate diff if extremely large
        diff_payload = diff
        truncated_note = ""
        if len(diff) > MAX_DIFF_CHARS:
            diff_payload = diff[:MAX_DIFF_CHARS]
            truncated_note = f"\n[Note: Diff was truncated to first {MAX_DIFF_CHARS} characters for size]"

        hint_section = ""
        if hint and hint.strip():
            hint_section = f"\nUser hint / additional context:\n{hint.strip()}\n"

        prompt = f"""You are an expert Git commit message generator.
Analyze the git diff below and write a clear, accurate, and professional commit message following Conventional Commits format (e.g. feat:, fix:, refactor:, chore:, docs:, test:, style:, perf:).

Guidelines:
1. First line: Imperative mood, conventional commit prefix, concise summary (under 72 chars).
2. If the diff contains non-trivial changes, leave a blank line and list 2-4 concise bullet points explaining what was changed and why.
3. Do NOT wrap output in markdown code blocks, backticks, or quotes. Output ONLY the raw commit message text.
{hint_section}
Here is the git diff:{truncated_note}
{diff_payload}
"""

        response = model.generate_content(prompt)
        if not response or not response.text:
            return None, "Model returned an empty response."

        message = clean_commit_message(response.text)
        return message, None

    except Exception as exc:
        return None, str(exc)
