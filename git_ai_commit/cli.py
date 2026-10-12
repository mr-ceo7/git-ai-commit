"""
Command line interface for git-ai-commit.
"""

import os
import sys
import argparse
import subprocess
import tempfile
import urllib.request
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from . import __version__
from .config import get_config_file, load_config, save_config, DEFAULT_MODEL
from .generator import generate_commit_message
from .git_utils import (
    commit_changes,
    get_current_branch,
    get_staged_diff,
    get_unstaged_files,
    has_remotes,
    has_staged_changes,
    is_git_repository,
    push_changes,
    stage_all,
    stage_files,
)

console = Console()
UPDATE_URL = "https://raw.githubusercontent.com/mr-ceo7/git-ai-commit/main/git-ai-commit"


def handle_config_command(args: argparse.Namespace) -> int:
    """Handle the config subcommand."""
    if args.set_key:
        cfg_path = save_config(api_key=args.set_key, model=args.set_model)
        console.print(f"[bold green]✓ Gemini API key saved to:[/bold green] {cfg_path}")
        return 0

    if args.set_model:
        api_key, _ = load_config()
        if not api_key:
            console.print("[yellow]Warning: Setting model without existing API key.[/yellow]")
        cfg_path = save_config(api_key=api_key or "", model=args.set_model)
        console.print(f"[bold green]✓ Model set to:[/bold green] {args.set_model} ({cfg_path})")
        return 0

    if args.show:
        api_key, model = load_config()
        masked_key = f"{api_key[:6]}...{api_key[-4:]}" if api_key and len(api_key) > 10 else (api_key or "Not set")
        console.print(Panel(
            f"[bold]Config File:[/bold] {get_config_file()}\n"
            f"[bold]Gemini Model:[/bold] {model}\n"
            f"[bold]API Key:[/bold] {masked_key}",
            title="git-ai-commit Configuration",
            border_style="cyan"
        ))
        return 0

    console.print("Usage: git-ai-commit config --set-key <API_KEY> | --set-model <MODEL> | --show")
    return 1


def handle_update() -> int:
    """Self-update the standalone executable in ~/.local/bin or current script."""
    console.print("[cyan]Checking for updates from GitHub...[/cyan]")
    target_path = os.path.expanduser("~/.local/bin/git-ai-commit")
    
    try:
        req = urllib.request.Request(
            UPDATE_URL,
            headers={"User-Agent": f"git-ai-commit/{__version__}"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()

        if not content:
            console.print("[red]Failed to fetch update: empty response.[/red]")
            return 1

        # Write to temporary file first
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        os.chmod(tmp_path, 0o755)
        os.replace(tmp_path, target_path)
        console.print(f"[bold green]✓ Successfully updated git-ai-commit at:[/bold green] {target_path}")
        return 0
    except Exception as exc:
        console.print(f"[red]Error during self-update: {exc}[/red]")
        return 1


def edit_message_in_editor(initial_text: str) -> str:
    """Open user's default editor (EDITOR/VISUAL or nano/vi) to edit commit message."""
    editor = os.getenv("VISUAL") or os.getenv("EDITOR") or ("nano" if os.name != "nt" else "notepad")
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w+", encoding="utf-8") as tf:
        tf.write(initial_text)
        tf_path = tf.name

    try:
        subprocess.run([editor, tf_path], check=True)
        with open(tf_path, "r", encoding="utf-8") as f:
            edited = f.read().strip()
        return edited or initial_text
    except Exception as err:
        console.print(f"[yellow]Warning: Could not open editor ({err}). Keeping original message.[/yellow]")
        return initial_text
    finally:
        if os.path.exists(tf_path):
            os.remove(tf_path)


def run_commit_flow(args: argparse.Namespace) -> int:
    """Main commit, generation, and push workflow."""
    api_key, default_model = load_config()
    if args.api_key:
        api_key = args.api_key
    model_name = args.model or default_model

    if not api_key:
        console.print("[bold red]Error: GEMINI_API_KEY is not configured.[/bold red]")
        console.print("Set your API key using one of:")
        console.print("  [cyan]git-ai-commit config --set-key YOUR_API_KEY[/cyan]")
        console.print("  [cyan]export GEMINI_API_KEY='YOUR_API_KEY'[/cyan]")
        console.print(f"  Or put it into [cyan]{get_config_file()}[/cyan]")
        return 1

    if not is_git_repository():
        console.print("[bold red]Error: Current directory is not a Git repository.[/bold red]")
        return 1

    # Staging phase
    if not args.no_stage:
        unstaged = get_unstaged_files()
        if unstaged:
            console.print(f"[cyan]Staging {len(unstaged)} modified/untracked file(s)...[/cyan]")
            ok, err = stage_all()
            if not ok:
                console.print(f"[bold red]Error staging files:[/bold red] {err}")
                return 1

    if not has_staged_changes():
        console.print("[yellow]Working tree clean: no staged changes to commit.[/yellow]")
        return 0

    diff = get_staged_diff()
    if not diff or not diff.strip():
        console.print("[yellow]No staged differences found.[/yellow]")
        return 0

    # Dry-run or message generation
    while True:
        with console.status("[bold cyan]Generating commit message with Gemini...[/bold cyan]", spinner="dots"):
            message, err = generate_commit_message(
                diff=diff,
                api_key=api_key,
                model_name=model_name,
                hint=args.hint
            )

        if err or not message:
            console.print(f"[bold red]Error generating commit message:[/bold red] {err}")
            return 1

        console.print(Panel(
            f"[bold green]{message}[/bold green]",
            title=f"Generated Commit Message ({model_name})",
            border_style="green"
        ))

        if args.dry_run:
            console.print("[yellow]Dry-run mode: skipping commit and push.[/yellow]")
            return 0

        if args.interactive:
            choice = Prompt.ask(
                "Action",
                choices=["commit", "edit", "regenerate", "abort"],
                default="commit"
            )
            if choice == "abort":
                console.print("[yellow]Commit aborted by user.[/yellow]")
                return 0
            elif choice == "regenerate":
                console.print("[cyan]Regenerating...[/cyan]")
                continue
            elif choice == "edit":
                message = edit_message_in_editor(message)
                console.print(f"[bold green]Updated Message:[/bold green]\n{message}")
                break
            else:
                break
        else:
            break

    # Commit phase
    console.print("[cyan]Committing changes...[/cyan]")
    ok, err = commit_changes(message)
    if not ok:
        console.print(f"[bold red]Error committing changes:[/bold red]\n{err}")
        return 1

    console.print("[bold green]✓ Changes committed successfully![/bold green]")

    # Push phase (default is to push, unless --no-push is provided)
    should_push = not args.no_push
    if should_push and args.interactive:
        should_push = Confirm.ask("Push changes to remote repository?", default=True)

    if should_push:
        if not has_remotes():
            console.print("[yellow]No git remote configured. Skipping push.[/yellow]")
            return 0

        current_branch = get_current_branch()
        console.print(f"[cyan]Pushing changes to remote ({current_branch})...[/cyan]")
        ok, err = push_changes()
        if not ok:
            console.print(f"[bold red]Error pushing changes:[/bold red]\n{err}")
            return 1
        console.print("[bold green]✓ Changes pushed successfully![/bold green]")
    else:
        console.print("[dim]Skipping push (--no-push active).[/dim]")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="git-ai-commit",
        description="AI-powered Git commit generator and auto-sync tool using Google Gemini"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-m", "--hint",
        dest="hint",
        type=str,
        help="Provide a hint or context to guide the generated commit message"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Interactive mode: confirm/edit message and confirm push"
    )
    parser.add_argument(
        "-n", "--no-push",
        action="store_true",
        help="Commit changes but do not push to remote repository"
    )
    parser.add_argument(
        "--no-stage",
        action="store_true",
        help="Only commit changes that are already staged (do not auto-stage unstaged files)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate commit message and display diff without committing or pushing"
    )
    parser.add_argument(
        "--model",
        type=str,
        help=f"Override Gemini model (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Override Gemini API key for this run"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Self-update git-ai-commit to the latest version from GitHub"
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # config subcommand
    config_parser = subparsers.add_parser("config", help="Manage configuration and API key")
    config_parser.add_argument("--set-key", type=str, help="Save Gemini API key")
    config_parser.add_argument("--set-model", type=str, help="Save default Gemini model")
    config_parser.add_argument("--show", action="store_true", help="Display current configuration")

    # update subcommand
    subparsers.add_parser("update", help="Update git-ai-commit to latest release")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.update or args.subcommand == "update":
        sys.exit(handle_update())

    if args.subcommand == "config":
        sys.exit(handle_config_command(args))

    sys.exit(run_commit_flow(args))


if __name__ == "__main__":
    main()
