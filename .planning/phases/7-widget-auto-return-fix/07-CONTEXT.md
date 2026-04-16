# Phase 7: Widget Auto-Return Fix - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix the zsh widget UX so the shell prompt automatically returns to a ready state after `??` displays explanation output. The user should not need to press Enter or Ctrl+C after viewing the explanation.

This phase does NOT change the keybinding (remains Ctrl+X ?), the CLI output format (remains WHY/FIX), or the skip-list behavior.

</domain>

<decisions>
## Implementation Decisions

### ZLE Refresh Strategy

- **D-01:** Use `zle reset-prompt` + `zle -R` pattern (standard zsh full reset)
- **D-02:** Execute reset after CLI completes — widget calls CLI, waits for exit, then resets
- **Rationale:** `reset-prompt` redraws the prompt line, `-R` redisplays any pending input buffer. Together they provide clean prompt return without flicker.

### Output Capture Method

- **D-03:** Direct print — CLI prints to stdout, no widget-side buffering
- **D-04:** Widget does not capture or manipulate CLI output
- **Rationale:** Simpler implementation. The ZLE reset after CLI completes handles clean return without needing to intercept output.

### Edge Case Handling

- **D-05:** CLI handles all edge cases (empty output, errors, line endings)
- **D-06:** CLI must ensure output ends with trailing newline
- **D-07:** Skip-list "nothing to explain" messages pass through unchanged
- **D-08:** Offline messages ("[explainer offline]") pass through unchanged
- **Rationale:** CLI already has appropriate messages for each edge case. Widget remains simple and doesn't duplicate logic.

### Buffer State Preservation

- **D-09:** Preserve user's pending input buffer after output displays
- **D-10:** `zle -R` automatically redisplays any typed-but-not-entered text
- **Rationale:** If user typed `ls -la` then pressed `??`, after explanation they see `ls -la` still in buffer ready to submit. No input is lost.

### Claude's Discretion

- Exact placement of ZLE calls in widget function
- Whether to add newline before or after output
- Error handling if ZLE commands fail (rare edge case)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Widget Implementation
- `errormux.plugin.zsh` — Current widget implementation, hook registration pattern
- `errormux.plugin.zsh:67-83` — Existing `_errormux_explain` widget function

### CLI Output
- `src/errormux/cli.py` — Python CLI entry point, output formatting
- `src/errormux/cli.py:88-94` — WHY/FIX output format

### Requirements
- `.planning/REQUIREMENTS.md` — WUX-01, WUX-02 acceptance criteria

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `errormux.plugin.zsh` — Widget registration pattern at lines 98-103 can be extended
- `zle -N` widget creation — Already used, just need to modify widget body
- `bindkey '^X?'` — Keybinding already set, no changes needed

### Established Patterns
- Hook registration via `preexec_functions+=()` and `precmd_functions+=()` pattern
- Widget function naming: `_errormux_<action>()`
- ZLE widget registration: `zle -N <widget-name> <function-name>`

### Integration Points
- Widget function `_errormux_explain` at line 67 — modification target
- CLI call at line 82 (`errormux`) — this is where we add ZLE reset after
- Python CLI outputs via Rich Console — ensure trailing newline

</code_context>

<specifics>
## Specific Ideas

- The fix should feel invisible — user presses `??`, sees explanation, and is immediately ready to type next command
- No flicker or visual artifacts during reset
- Works identically whether user had pending input or empty buffer

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 07-widget-auto-return-fix*
*Context gathered: 2026-04-16*
