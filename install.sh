#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# ErrorMux Installer
# ==============================================================================
# Single-command installer for the ErrorMux zsh plugin.
# Usage: curl -sSL https://.../install.sh | bash
#   or:  git clone https://github.com/YOUR_USERNAME/errormux.git && ./install.sh
# ==============================================================================

INSTALL_DIR="$HOME/.shell-explainer"
PLUGIN_FILE="$INSTALL_DIR/errormux.plugin.zsh"
SOURCE_LINE="source ~/.shell-explainer/errormux.plugin.zsh"
REPO_URL="https://github.com/YOUR_USERNAME/errormux.git"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

info() { echo -e "${GREEN}[errormux]${NC} $1"; }
warn() { echo -e "${YELLOW}[errormux warning]${NC} $1"; }
error() { echo -e "${RED}[errormux error]${NC} $1"; exit 1; }

# ==============================================================================
# Pre-flight Checks
# ==============================================================================

info "Running pre-flight checks..."

# Check for uv (required for Python dependency management)
if ! command -v uv >/dev/null 2>&1; then
    error "uv is required but not installed.\n\nPlease install uv first:\n  curl -sSL https://astral.sh/uv/install.sh | sh\n\nSee: https://docs.astral.sh/uv/"
fi

# Check for git (required for cloning)
if ! command -v git >/dev/null 2>&1; then
    error "git is required but not installed."
fi

# ==============================================================================
# Clone or Update Repository
# ==============================================================================

if [[ -d "$INSTALL_DIR/.git" ]]; then
    info "Updating existing installation..."
    git -C "$INSTALL_DIR" pull || warn "Failed to pull updates, continuing with existing version..."
else
    info "Cloning errormux to $INSTALL_DIR..."
    # Remove incomplete/broken installation if it exists
    if [[ -d "$INSTALL_DIR" ]]; then
        warn "Removing incomplete installation..."
        rm -rf "$INSTALL_DIR"
    fi
    git clone "$REPO_URL" "$INSTALL_DIR" || error "Failed to clone repository. Check the URL: $REPO_URL"
fi

# Verify plugin file exists
if [[ ! -f "$PLUGIN_FILE" ]]; then
    error "Plugin file not found after clone: $PLUGIN_FILE"
fi

info "Plugin installed successfully."

# ==============================================================================
# .zshrc Modification
# ==============================================================================

# Create .zshrc if it doesn't exist
if [[ ! -f ~/.zshrc ]]; then
    info "Creating ~/.zshrc..."
    touch ~/.zshrc
fi

# Check if source line already exists (D-07: grep -qF for exact match)
if grep -qF "$SOURCE_LINE" ~/.zshrc 2>/dev/null; then
    info ".zshrc already configured."
else
    info "Adding source line to .zshrc..."
    echo "" >> ~/.zshrc
    echo "# ErrorMux - on-demand error explanations" >> ~/.zshrc
    echo "$SOURCE_LINE" >> ~/.zshrc
fi

# ==============================================================================
# Python Dependencies
# ==============================================================================

info "Installing Python dependencies..."
cd "$INSTALL_DIR"
uv sync || error "Failed to install Python dependencies with 'uv sync'."

# ==============================================================================
# Success Message
# ==============================================================================

echo ""
info "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Open a new terminal (or run: source ~/.zshrc)"
echo "  2. Run a command that fails"
echo "  3. Type ?? for an explanation"
echo ""
echo "Files:"
echo "  Plugin:     ~/.shell-explainer/errormux.plugin.zsh"
echo "  Config:     ~/.shell-explainer/config.toml"
echo "  Cache:      ~/.shell-explainer/cache.db"
echo ""
