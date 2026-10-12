"""
Configuration management for git-ai-commit.
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from dotenv import dotenv_values, load_dotenv

CONFIG_DIR = Path.home() / ".config" / "git-ai-commit"
CONFIG_FILE = CONFIG_DIR / ".env"
LEGACY_CONFIG = Path("/usr/local/bin/.env")
DEFAULT_MODEL = "gemini-2.5-flash"


def get_config_file() -> Path:
    return CONFIG_FILE


def load_config() -> Tuple[Optional[str], str]:
    """
    Load GEMINI_API_KEY and GEMINI_MODEL with the following priority:
    1. os.environ
    2. ~/.config/git-ai-commit/.env
    3. Current working directory .env
    4. /usr/local/bin/.env (legacy fallback)
    """
    # First load ~/.config/git-ai-commit/.env if it exists
    if CONFIG_FILE.is_file():
        load_dotenv(dotenv_path=CONFIG_FILE)

    # Next load current directory .env if present
    cwd_env = Path.cwd() / ".env"
    if cwd_env.is_file():
        load_dotenv(dotenv_path=cwd_env)

    # Next check legacy /usr/local/bin/.env if still not in os.environ
    if "GEMINI_API_KEY" not in os.environ and LEGACY_CONFIG.is_file():
        load_dotenv(dotenv_path=LEGACY_CONFIG)

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    return api_key, model


def save_config(api_key: str, model: Optional[str] = None) -> Path:
    """Save API key and optional model to ~/.config/git-ai-commit/.env with safe permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    current_model = model or DEFAULT_MODEL
    if CONFIG_FILE.is_file():
        existing = dotenv_values(CONFIG_FILE)
        if not model and "GEMINI_MODEL" in existing:
            current_model = existing["GEMINI_MODEL"]

    content = f"# git-ai-commit configuration\nGEMINI_API_KEY={api_key.strip()}\nGEMINI_MODEL={current_model.strip()}\n"
    
    CONFIG_FILE.write_text(content, encoding="utf-8")
    CONFIG_FILE.chmod(0o600)
    return CONFIG_FILE
