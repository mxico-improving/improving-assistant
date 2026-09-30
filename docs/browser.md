# Browser access

The skills need a real, visible browser where **you** are signed in to Engage and Workday. There
are two ways to get one. The skills pick one automatically.

## Option A: Claude in Chrome (recommended for Claude Code)

Claude Code's official Chrome integration drives your normal Chrome or Edge, using your existing
logins. When it reaches a login page or MFA prompt, it pauses and asks you to handle it.

Requirements (from the Claude Code docs):
- A direct Anthropic plan: Pro, Max, Team or Enterprise, signed in with `/login`.
  **API-key or `setup-token` auth disables it.** Use Option B then.
- Google Chrome or Microsoft Edge (other Chromium browsers are detected too). Not supported in WSL.
- The "Claude in Chrome" extension (v1.0.36+) from the Chrome Web Store.

Setup:
1. Install the extension: https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn
2. Start Claude Code with `claude --chrome`, or run `/chrome` and pick "Enabled by default".
3. Check with `/chrome`. It should show "Status: Enabled" and "Extension: Installed".
4. In Chrome, sign in once to https://engage.improving.com and https://workday.improving.com.

## Option B: `ia.py browser` (fallback, works everywhere)

A stdlib-only DevTools client in this plugin. It drives a separate Chrome window with its own
profile (`~/.improving-assistant/chrome-profile`), so your personal profile isn't touched and
sessions persist between runs. Use it when Claude in Chrome isn't available (API-key auth, Hermes,
WSL, or the extension isn't installed).

    python3 ia.py browser start              # opens Chrome with Engage + Workday tabs, then you sign in
    python3 ia.py browser tabs               # list tabs
    python3 ia.py browser eval engage "document.title"
    python3 ia.py browser click myworkday "Save and Close"   # real mouse click by exact visible text
    python3 ia.py browser type myworkday "10052026"          # real key events into the focused field
    python3 ia.py browser shot engage shot.png

`TAB` is a substring of the tab's URL or title (`engage`, `myworkday`). DevTools listens only on
127.0.0.1:9333. **Never headless**: Engage's Cloudflare check blocks headless and automated
browsers, so a visible window is required.

## Rules for both options
- You sign in and approve MFA yourself. The assistant never types passwords or codes.
- Workday ignores synthetic JS `.click()` and `.value` changes, so use real mouse and key events.
  Claude in Chrome does this natively. Option B's `click` and `type` do it too.
- Sessions expire a few times a day. If a login page shows up mid-flow, stop, ask the user to
  sign in, then continue.
