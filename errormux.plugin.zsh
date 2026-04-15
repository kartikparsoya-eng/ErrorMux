#!/usr/bin/env zsh
# errormux.plugin.zsh - zsh plugin for on-demand error explanations
# 
# This plugin captures command context via preexec/precmd hooks and provides
# a `??` widget for user-triggered explanations.
#
# Installation: source this file in ~/.zshrc
#   source /path/to/errormux.plugin.zsh

# ==============================================================================
# Global State
# ==============================================================================

_ERRORMUX_LAST_CMD=""
_ERRORMUX_LAST_EXIT=0
_ERRORMUX_LAST_STDERR=""
_ERRORMUX_STDERR_FILE="/tmp/shell-explainer-last-stderr"

# ==============================================================================
# Initialization
# ==============================================================================

# Clear stale state on plugin load
: > /tmp/shell-explainer-last-cmd
: > "$_ERRORMUX_STDERR_FILE"
echo "0" > /tmp/shell-explainer-last-exit

# ==============================================================================
# Hook Functions
# ==============================================================================

# CAPT-01, CAPT-02: Capture command text and set up stderr redirect
# preexec runs BEFORE each command execution
# $3 contains the full command text (user-typed + expanded)
_errormux_preexec() {
    # Capture command text (CAPT-01)
    _ERRORMUX_LAST_CMD="$3"
    
    # Clear previous stderr
    : > "$_ERRORMUX_STDERR_FILE"
    
    # Redirect stderr through tee (CAPT-02, D-01, D-02)
    # This captures stderr to file while preserving terminal output
    exec 2> >(tee "$_ERRORMUX_STDERR_FILE" >&2)
}

# CAPT-03: Capture exit code after command completes
# precmd runs AFTER each command, before prompt display
_errormux_precmd() {
    # Capture exit code (CAPT-03)
    _ERRORMUX_LAST_EXIT=$?
    
    # Read captured stderr (may have trailing newline)
    _ERRORMUX_LAST_STDERR=$(cat "$_ERRORMUX_STDERR_FILE" 2>/dev/null || echo "")
    
    # Write state to tmp files for widget access
    printf '%s' "$_ERRORMUX_LAST_CMD" > /tmp/shell-explainer-last-cmd
    printf '%s' "$_ERRORMUX_LAST_STDERR" > /tmp/shell-explainer-last-stderr
    echo "$_ERRORMUX_LAST_EXIT" > /tmp/shell-explainer-last-exit
}

# ==============================================================================
# Widget Function
# ==============================================================================

# CAPT-04, CAPT-05: User-triggered explanation via `??` keybinding
_errormux_explain() {
    # Read last exit code from tmp file
    local exit_code
    exit_code=$(cat /tmp/shell-explainer-last-exit 2>/dev/null || echo "0")
    
    # CAPT-05: Skip explanation for non-error exit codes
    # 0 = success
    # 130 = SIGINT (Ctrl+C)
    # 148 = SIGTSTP (Ctrl+Z) on Linux
    if [[ "$exit_code" -eq 0 ]] || [[ "$exit_code" -eq 130 ]] || [[ "$exit_code" -eq 148 ]]; then
        return 0
    fi
    
    # CAPT-04: Invoke Python CLI (stub in Phase 1)
    # Real implementation with Ollama integration comes in Phase 2
    errormux explain
}

# ==============================================================================
# Hook Registration
# ==============================================================================

# Register hooks using array pattern (avoids conflicts with other plugins)
# This is the zsh-standard approach per PITFALLS.md Pitfall 5
preexec_functions+=(_errormux_preexec)
precmd_functions+=(_errormux_precmd)

# ==============================================================================
# Widget Registration
# ==============================================================================

# Create zle widget and bind to `??` key sequence
zle -N errormux-explain _errormux_explain
bindkey '??' errormux-explain
