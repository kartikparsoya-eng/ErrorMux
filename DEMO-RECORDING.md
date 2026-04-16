# Demo Recording Guide

This document describes how to record the ErrorMux demo GIF.

## Prerequisites

- Node.js and npm installed
- terminalizer installed globally

## Installation

```bash
npm install -g terminalizer
```

## Recording Steps

### 1. Open a fresh terminal
Start a new terminal session with ErrorMux loaded.

### 2. Record the demo
```bash
terminalizer record demo -k
```

The `-k` flag keeps the configuration file after recording.

### 3. Perform the demo actions
When recording starts:
1. Type a command that will fail: `ls /nonexistent`
2. Press Enter to see the error
3. Type `??` to trigger ErrorMux
4. Wait for the explanation to appear
5. Press Enter to return to clean prompt
6. Press Ctrl+D to stop recording

### 4. Render the GIF
```bash
terminalizer render demo -o demo.gif
```

### 5. Move to repository root
```bash
mv demo.gif /path/to/ErrorMux/
```

## Customization (Optional)

Edit `demo.yml` (created during recording) to customize:
- Frame delay
- Font size
- Theme colors
- Window padding

Then re-render:
```bash
terminalizer render demo -o demo.gif -c demo.yml
```

## Best Practices

- Keep the demo under 30 seconds
- Use a clean terminal theme (dark background recommended)
- Ensure terminal window is appropriately sized
- Run the sequence once before recording to verify timing

## Troubleshooting

**Issue:** terminalizer not found
**Solution:** Ensure npm global bin directory is in PATH:
```bash
npm config get prefix
export PATH="$PATH:$(npm config get prefix)/bin"
```

**Issue:** GIF is too large
**Solution:** Reduce frame rate or trim frames in `demo.yml`

## After Recording

1. Verify demo.gif is in repository root
2. Update README.md to include the demo:
   ```markdown
   ## Demo
   
   ![ErrorMux Demo](demo.gif)
   ```
3. Commit and push to GitHub
