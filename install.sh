#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# ErrorMux Installer
# ==============================================================================
# Single-command installer for the ErrorMux zsh plugin.
# Usage: curl -sSL https://.../install.sh | bash
#   or:  git clone https://github.com/kartikparsoya-eng/ErrorMux.git && ./install.sh
#
# Detects Oh My Zsh and uses appropriate plugin path automatically.
# ==============================================================================

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

info() { echo -e "${GREEN}[errormux]${NC} $1"; }
warn() { echo -e "${YELLOW}[errormux warning]${NC} $1"; }
error() { echo -e "${RED}[errormux error]${NC} $1"; exit 1; }

# ==============================================================================
# Oh My Zsh Detection (T-01)
# ==============================================================================

detect_omz_path() {
    # Primary: Check ZSH_CUSTOM env var
    if [[ -n "${ZSH_CUSTOM:-}" ]]; then
        echo "${ZSH_CUSTOM}/plugins/errormux"
        return 0
    fi
    
    # Fallback: Check standard Oh My Zsh custom plugins path
    if [[ -d "$HOME/.oh-my-zsh/custom/plugins" ]]; then
        echo "$HOME/.oh-my-zsh/custom/plugins/errormux"
        return 0
    fi
    
    # Not found
    return 1
}

# ==============================================================================
# Detect Install Path (T-02, T-04)
# ==============================================================================

REPO_URL="https://github.com/kartikparsoya-eng/ErrorMux.git"

if OMZ_PATH=$(detect_omz_path); then
    INSTALL_DIR="$OMZ_PATH"
    IS_OMZ=true
else
    INSTALL_DIR="$HOME/.shell-explainer"
    IS_OMZ=false
fi

PLUGIN_FILE="$INSTALL_DIR/errormux.plugin.zsh"
SOURCE_LINE="source $PLUGIN_FILE"

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
# .zshrc Modification (T-03)
# ==============================================================================

# Create .zshrc if it doesn't exist
if [[ ! -f ~/.zshrc ]]; then
    info "Creating ~/.zshrc..."
    touch ~/.zshrc
fi

if [[ "$IS_OMZ" == "true" ]]; then
    # Oh My Zsh: Check if already in plugins
    if grep -qF "errormux" ~/.zshrc 2>/dev/null; then
        info ".zshrc already configured."
    else
        info "Oh My Zsh detected!"
        info "Add 'errormux' to your plugins array in ~/.zshrc:"
        echo ""
        echo "  plugins=(git errormux ...)"
        echo ""
    fi
else
    # Non-Oh My Zsh: Use source line (existing logic)
    if grep -qF "$SOURCE_LINE" ~/.zshrc 2>/dev/null; then
        info ".zshrc already configured."
    else
        info "Adding source line to .zshrc..."
        echo "" >> ~/.zshrc
        echo "# ErrorMux - on-demand error explanations" >> ~/.zshrc
        echo "$SOURCE_LINE" >> ~/.zshrc
    fi
fi

# ==============================================================================
# Python Dependencies
# ==============================================================================

info "Installing Python dependencies..."
cd "$INSTALL_DIR"
uv sync || error "Failed to install Python dependencies with 'uv sync'."

# ==============================================================================
# Success Message (T-06)
# ==============================================================================

echo ""
info "✓ Installation complete!"
echo ""
if [[ "$IS_OMZ" == "true" ]]; then
    echo "Oh My Zsh installed to: $INSTALL_DIR"
    echo ""
    echo "Next steps:"
    echo "  1. Add 'errormux' to plugins in ~/.zshrc"
    echo "  2. Open a new terminal (or run: source ~/.zshrc)"
    echo "  3. Run a command that fails"
    echo "  4. Press Alt+E for an explanation"
else
    echo "Files:"
    echo "  Plugin:     $PLUGIN_FILE"
    echo "  Config:     ~/.shell-explainer/config.toml"
    echo "  Cache:      ~/.shell-explainer/cache.db"
    echo ""
    echo "Next steps:"
    echo "  1. Open a new terminal (or run: source ~/.zshrc)"
    echo "  2. Run a command that fails"
    echo "  3. Type ?? for an explanation"
fi
echo ""
