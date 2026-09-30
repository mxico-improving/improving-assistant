---
name: engage-log
description: Use when the user wants to record an activity in Improving Engage (engage.improving.com), e.g. "log that I mentored Ana yesterday" or "add my talk from Friday to Engage". Maps the description to category/type, confirms, then submits.
argument-hint: "[what you did, when]"
---

# Log an Engage activity

Records one activity in https://engage.improving.com ("Add Activity" form).

Form fields: Activity Category, Activity Type (options depend on the category),
Date (MM/DD/YYYY), Quantity (default 1), Notes. The button reads "Add N points".

## Browser (pick one before submitting; see `${CLAUDE_PLUGIN_ROOT}/docs/browser.md`)
- **Claude in Chrome** (preferred): if browser tools are available (`/chrome` shows Enabled),
  use them. They drive the user's own Chrome, where they're already signed in.
- **Fallback** (API-key auth, Hermes, WSL, no extension): use the plugin's own client.
  `python3 "${CLAUDE_PLUGIN_ROOT}/ia.py" browser tabs` (if it can't connect: `... browser start`
  and ask the user to sign in), then `browser eval|click|type|shot <tab> ...`.
Either way: if a tab shows a login page (`/account/login`, `login.microsoftonline.com`,
`authgwy/.../login`), stop and ask the user to sign in and approve MFA, then continue.

## Steps

1. Parse the request ($ARGUMENTS): what happened, the date (resolve "yesterday"/"Friday"
   to a real date and state it), quantity, and anything useful for Notes.

2. Pick the Category and Type from the list in `${CLAUDE_PLUGIN_ROOT}/docs/engage.md`. If that list is missing
   or nothing fits clearly, open the form and read the live dropdown options. Offer the
   2-3 closest matches and let the user choose. Never pick an ambiguous type silently.

3. Show the full entry (category, type, date, quantity, notes, and the points shown
   on the button) and wait for an explicit "OK".

4. Submit in the browser. If Microsoft sign-in asks for MFA, ask the user to approve it
   on their phone and wait. Never type passwords or codes yourself.

5. Confirm the activity appears in the list and report the points added.

Don't use this for the weekly "full week" activity. /weekly-checkin handles that,
because it depends on PTO and holidays.
