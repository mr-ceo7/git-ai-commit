# git-ai-commit 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: >=3.8](https://img.shields.io/badge/Python->=3.8-brightgreen.svg)](https://www.python.org/)
[![CLI: Git & GH](https://img.shields.io/badge/Integration-Git%20%7C%20GH%20CLI-orange.svg)](#installation)

An intelligent, AI-powered Git commit generator and automatic synchronization tool powered by **Google Gemini**.

`git-ai-commit` analyzes your staged and unstaged code changes, generates clean, descriptive commit messages adhering to the **Conventional Commits** specification, commits the changes, and pushes directly to your remote repository in a single command.

---

## ✨ Features

- 🧠 **Smart Message Generation**: Inspects git diffs and writes structured conventional commit messages (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, etc.) using Google Gemini.
- ⚡ **Zero-Friction Workflow**: Automatically detects modified/untracked files, stages them, commits with the AI message, and pushes to remote.
- 🔌 **Universal Invocation**: Works seamlessly as:
  - `git ai-commit` (native Git subcommand)
  - `git-ai-commit` (standalone CLI tool)
  - `gh ai-commit` (GitHub CLI extension)
- 🎛️ **Interactive Mode (`-i`)**: Review, edit, or regenerate commit messages before committing, with prompt confirmation before pushing.
- 🧪 **Dry Run (`--dry-run`)**: Preview generated messages and diff analysis without making any git changes.
- 💬 **Context Hints (`-m "..."`)**: Guide the AI generator with additional instructions or business context.
- 🔐 **Secure Configuration**: Stores credentials in `~/.config/git-ai-commit/.env` with strict `0600` permissions.
- 🔄 **One-Command Updates**: Update directly from GitHub using `git-ai-commit update`.

---

## 📦 Installation

### One-Line Install (Recommended)

Run the installer directly in your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/mr-ceo7/git-ai-commit/main/install.sh | bash
```

This installs `git-ai-commit` and `gh-ai-commit` into `~/.local/bin/`.

### Via GitHub CLI (`gh`)

```bash
gh extension install mr-ceo7/git-ai-commit
```

### From Source

```bash
git clone https://github.com/mr-ceo7/git-ai-commit.git
cd git-ai-commit
./install.sh
```

Or install with `pip`:

```bash
pip install -e .
```

---

## ⚙️ Configuration

`git-ai-commit` requires a Google Gemini API key. You can get one for free at [Google AI Studio](https://aistudio.google.com/).

### 1. Set via CLI (Saved to `~/.config/git-ai-commit/.env`)

```bash
git-ai-commit config --set-key "AIzaSy..."
```

### 2. Set via Environment Variable

```bash
export GEMINI_API_KEY="AIzaSy..."
```

### 3. Check Configuration

```bash
git-ai-commit config --show
```

---

## 🚀 Usage

### Standard Workflow (Auto-stage, Commit & Push)

Inside any git repository:

```bash
git ai-commit
```

Or:

```bash
git-ai-commit
```

Or via GitHub CLI:

```bash
gh ai-commit
```

### Common Workflows

#### 1. Interactive Review (`-i`)
Review the generated message with options to commit, edit in your text editor, regenerate, or abort:

```bash
git ai-commit -i
```

#### 2. Commit Without Pushing (`-n` / `--no-push`)
Generate AI message and commit locally, without pushing to the remote branch:

```bash
git ai-commit -n
```

#### 3. Preview without Committing (`--dry-run`)
View the staged diff and generated commit message without making changes:

```bash
git ai-commit --dry-run
```

#### 4. Add Context or Guidance (`-m` / `--hint`)
Guide the AI when making specific architectural or domain-specific changes:

```bash
git ai-commit -m "Refactor token rotation to use atomic locks"
```

#### 5. Commit Already-Staged Files Only (`--no-stage`)
By default, `git-ai-commit` stages all modified files. Use `--no-stage` to only commit files you manually added with `git add`:

```bash
git add src/core.py
git ai-commit --no-stage
```

---

## 🛠️ CLI Reference

```
usage: git-ai-commit [-h] [-v] [-m HINT] [-i] [-n] [--no-stage] [--dry-run]
                     [--model MODEL] [--api-key API_KEY] [--update]
                     {config,update} ...

AI-powered Git commit generator and auto-sync tool using Google Gemini

positional arguments:
  {config,update}       Available subcommands
    config              Manage configuration and API key
    update              Update git-ai-commit to latest release

options:
  -h, --help            Show this help message and exit
  -v, --version         Show program's version number and exit
  -m, --hint HINT       Provide a hint or context to guide the generated commit message
  -i, --interactive     Interactive mode: confirm/edit message and confirm push
  -n, --no-push         Commit changes but do not push to remote repository
  --no-stage            Only commit changes that are already staged
  --dry-run             Generate commit message and display diff without committing or pushing
  --model MODEL         Override Gemini model (default: gemini-2.5-flash)
  --api-key API_KEY     Override Gemini API key for this run
  --update              Self-update git-ai-commit to the latest version from GitHub
```

---

## 🗑️ Uninstallation

To remove `git-ai-commit` from your system:

```bash
curl -fsSL https://raw.githubusercontent.com/mr-ceo7/git-ai-commit/main/uninstall.sh | bash
```

Or from a local clone:

```bash
./uninstall.sh
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

Developed with ❤️ by [mr-ceo7](https://github.com/mr-ceo7).
