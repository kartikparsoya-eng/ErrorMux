#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# ErrorMux Uninstaller
# ==============================================================================

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[errormux]${NC} $1"; }
warn() { echo -e "${YELLOW}[errormux warning]${NC} $1"; }
error() { echo -e "${RED}[errormux error]${NC} $1"; exit 1; }

# ==============================================================================
# Detect Installation Location
# ==============================================================================

detect_install_dir() {
    # Check Oh My Zsh path first
    if [[ -n "${ZSH_CUSTOM:-}" ]] && [[ -d "${ZSH_CUSTOM}/plugins/errormux" ]]; then
        echo "${ZSH_CUSTOM}/plugins/errormux"
        return 0
    fi
    
    if [[ -d "$HOME/.oh-my-zsh/custom/plugins/errormux" ]]; then
        echo "$HOME/.oh-my-zsh/custom/plugins/errormux"
        return 0
    fi
    
    # Check default path
    if [[ -d "$HOME/.shell-explainer" ]]; then
        echo "$HOME/.shell-explainer"
        return 0
    fi
    
    return 1
}

# ==============================================================================
# Main
# ==============================================================================

echo ""
info "ErrorMux Uninstaller"
echo ""

if ! INSTALL_DIR=$(detect_install_dir); then
    error "ErrorMux installation not found."
fi

info "Found installation at: $INSTALL_DIR"

# Confirm removal
echo ""
echo "This will remove:"
echo "  - $INSTALL_DIR"
echo "  - ~/.shell-explainer/config.toml (if exists)"
echo "  - ~/.shell-explainer/cache.db (if exists)"
echo ""
read -p "Continue? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    info "Cancelled."
    exit 0
fi

# Remove plugin directory
info "Removing plugin directory..."
rm -rf "$INSTALL_DIR"

# Remove config/cache if in default location
if [[ -d "$HOME/.shell-explainer" ]]; then
    info "Removing config and cache..."
    rm -rf "$HOME/.shell-explainer"
fi

# Success
echo ""
info "✓ Uninstallation complete!"
echo ""
echo "Manual cleanup required in ~/.zshrc:"
echo ""
if [[ "$INSTALL_DIR" =~ "oh-my-zsh" ]]; then
    echo "  1. Remove 'errormux' from your plugins array"
else
    echo "  1. Remove the 'source ~/.shell-explainer/errormux.plugin.zsh' line"
fi
echo ""
echo "Then open a new terminal or run: source ~/.zshrc"
echo ""
