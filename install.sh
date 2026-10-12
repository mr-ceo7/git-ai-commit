#!/usr/bin/env bash
# ==============================================================================
# git-ai-commit installer
# Installs git-ai-commit into ~/.local/bin/git-ai-commit
# Works as:
#   - git-ai-commit
#   - git ai-commit
#   - gh ai-commit
# ==============================================================================

set -e

REPO_RAW_URL="https://raw.githubusercontent.com/mr-ceo7/git-ai-commit/main"
TARGET_DIR="${HOME}/.local/bin"
TARGET_BIN="${TARGET_DIR}/git-ai-commit"
GH_BIN="${TARGET_DIR}/gh-ai-commit"

echo "=== Installing git-ai-commit ==="

# 1. Verify Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required but not installed." >&2
    exit 1
fi

# 2. Check essential Python packages
echo "Verifying Python dependencies..."
MISSING_PKGS=()
for pkg in "google.generativeai" "dotenv" "rich"; do
    if ! python3 -c "import ${pkg}" >/dev/null 2>&1; then
        MISSING_PKGS+=("${pkg}")
    fi
done

if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    echo "Installing missing dependencies: ${MISSING_PKGS[*]}..."
    python3 -m pip install --quiet --user google-generativeai python-dotenv rich inquirer || {
        echo "Warning: Could not automatically install Python packages via pip."
        echo "Run: pip install google-generativeai python-dotenv rich inquirer"
    }
fi

# 3. Ensure ~/.local/bin exists
mkdir -p "${TARGET_DIR}"

# 4. Install binary (from local repo clone if present, otherwise download)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
if [ -f "${SCRIPT_DIR}/git-ai-commit" ]; then
    echo "Installing from local repository..."
    cp -f "${SCRIPT_DIR}/git-ai-commit" "${TARGET_BIN}"
else
    echo "Downloading git-ai-commit from GitHub..."
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "${REPO_RAW_URL}/git-ai-commit" -o "${TARGET_BIN}"
    elif command -v wget >/dev/null 2>&1; then
        wget -qO "${TARGET_BIN}" "${REPO_RAW_URL}/git-ai-commit"
    else
        echo "Error: Neither curl nor wget found." >&2
        exit 1
    fi
fi

chmod +x "${TARGET_BIN}"

# 5. Create GitHub CLI extension symlink & alias
ln -sf "${TARGET_BIN}" "${GH_BIN}"
if command -v gh >/dev/null 2>&1; then
    gh alias set ai-commit '!git-ai-commit "$@"' 2>/dev/null || true
    echo "✓ Configured GitHub CLI alias (gh ai-commit)"
fi

# 6. Initialize user config directory and migrate legacy config if present
CONFIG_DIR="${HOME}/.config/git-ai-commit"
mkdir -p "${CONFIG_DIR}"
if [ ! -f "${CONFIG_DIR}/.env" ] && [ -f "/usr/local/bin/.env" ]; then
    cp "/usr/local/bin/.env" "${CONFIG_DIR}/.env"
    chmod 600 "${CONFIG_DIR}/.env"
    echo "✓ Migrated existing Gemini credentials to ${CONFIG_DIR}/.env"
fi

echo "✓ Successfully installed to ${TARGET_BIN}"
echo "✓ Created GitHub CLI extension symlink: ${GH_BIN}"

# 7. Check PATH
case ":$PATH:" in
    *":${TARGET_DIR}:"*) ;;
    *)
        echo ""
        echo "Note: ${TARGET_DIR} is not in your \$PATH."
        echo "Add it to your shell configuration (~/.bashrc or ~/.zshrc):"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        ;;
esac

echo ""
echo "=== Ready to Use ==="
echo "You can now run:"
echo "  git ai-commit          # Native git integration"
echo "  git-ai-commit          # Standalone CLI tool"
echo "  gh ai-commit           # GitHub CLI extension"
echo ""
echo "Configuration:"
echo "  git-ai-commit config --set-key YOUR_GEMINI_API_KEY"
echo "  git-ai-commit config --show"
echo ""
