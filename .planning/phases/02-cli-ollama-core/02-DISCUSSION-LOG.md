# Phase 2: CLI + Ollama Core - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-15
**Phase:** 02-cli-ollama-core
**Areas discussed:** Prompt structure, Output formatting, Error handling

---

## Prompt Structure

| Option | Description | Selected |
|--------|-------------|----------|
| System + user messages | Use ollama.chat() with system prompt defining output format, user message with context | ✓ |
| Single formatted prompt | One concatenated string with instructions and context | |
| Template file | Load prompt template from a file | |

**User's choice:** System + user messages (Recommended)
**Notes:** Cleaner separation, follows best practices

---

| Option | Description | Selected |
|--------|-------------|----------|
| Labeled sections | Ask for WHY: <sentence>\nFIX: <command> | ✓ |
| JSON structure | Ask for {"why": "...", "fix": "..."} | |
| Markdown headers | Ask for ## WHY and ## FIX headers | |

**User's choice:** Labeled sections (Recommended)
**Notes:** Simple to parse with regex, works reliably with gemma3:4b

---

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal | Just explain that this is a shell error, ask for WHY/FIX format | |
| Shell-aware | Include that it's zsh, mention common patterns (pipes, redirects) | ✓ |
| Full context | Include OS info, shell version, PATH | |

**User's choice:** Shell-aware
**Notes:** Better for complex commands but larger prompts

---

## Output Formatting

| Option | Description | Selected |
|--------|-------------|----------|
| Stream | Use ollama.chat(stream=True), print chunks as they arrive | ✓ |
| Buffer then print | Wait for full response, then print formatted output | |

**User's choice:** Stream (Recommended)
**Notes:** Feels faster, better UX for longer explanations

---

| Option | Description | Selected |
|--------|-------------|----------|
| Buffer then format | Collect all streamed text, parse WHY/FIX after stream ends, then print with Rich | ✓ |
| Stream raw, then format | Print raw stream first, then reprint with formatting | |
| Live reformat | Use Rich Live to update display as sections are detected | |

**User's choice:** Buffer then format (Recommended)
**Notes:** Guarantees clean output

---

| Option | Description | Selected |
|--------|-------------|----------|
| Compact | WHY: <text>\nFIX: <command> — minimal spacing, two lines max | ✓ |
| Separated with divider | WHY: <text>\n───\nFIX: <command> | |
| Card-style with box | Draw Rich panel/box around the output | |

**User's choice:** Compact (Recommended)
**Notes:** Fits in terminal without scrolling

---

## Error Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Graceful offline | Print '[explainer offline]' and exit 0 | ✓ |
| Helpful hint | Print '[explainer offline] Run: ollama serve' | |
| Silent | Print nothing and exit 0 | |

**User's choice:** Graceful offline (Recommended)
**Notes:** Non-intrusive, matches PROJECT.md requirement

---

| Option | Description | Selected |
|--------|-------------|----------|
| Single timeout, then offline | Set 10s timeout on ollama.Client(), let it raise TimeoutException | ✓ |
| Progress indication | Show spinner/dots while waiting, then offline on timeout | |
| Retry once | On timeout, retry once before showing offline | |

**User's choice:** Single timeout, then offline (Recommended)
**Notes:** Simple, matches requirement

---

| Option | Description | Selected |
|--------|-------------|----------|
| Print raw output | If WHY/FIX not found, print the raw response | ✓ |
| Show fallback message | Print '[could not parse explanation]' and exit | |

**User's choice:** Print raw output (Recommended)
**Notes:** User still gets value even if format failed

---

## Claude's Discretion

- Exact wording of system prompt — planner to craft based on D-01, D-02, D-03
- Regex pattern for WHY/FIX parsing — planner to implement based on D-02
- Whether to use Rich Console or plain print with Rich markup — planner to choose

## Deferred Ideas

None — discussion stayed within phase scope.
