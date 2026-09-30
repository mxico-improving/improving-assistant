# Workday screen map

Status: MAPPED 2026-09-29, including a real end-to-end submit (week of Oct 4-10 2026).
Update this file when the UI changes.

## Access
- Instance: https://workday.improving.com, which redirects through Microsoft SSO
  (launcher.myapps.microsoft.com) to the Improving Workday tenant home page (`.../improving/d/home.htmld`)
- MFA (Authenticator push, number match, SMS or passkey) is always approved by the user.
- Sessions expire a few times a day. When the Microsoft sign-in page appears, pause and ask
  the user to approve.
- A "Your Session Has Been Recovered" dialog may appear on Home. Click "Not Now".

## Navigation
Home > MENU (`[data-automation-id=globalNavButton]`) > Personal > **Time**. The Time hub has:
- Enter Time: **This Week (N Hours)**, **Last Week (N Hours)**, **Select Week**
- View: My Schedule, My Time Off, Time Off Balance

"Select Week" opens a "Default Time Entry for Select Week" dialog with a date field split into
`dateSectionMonth-input` / `dateSectionDay-input` / `dateSectionYear-input`. Type the digits as
real key events: setting `.value` or using insertText leaves the field empty and gives
"The field Date is required". Any day of the week works. Then click OK (the last visible
OK button).

## "Enter Time by Type" grid (weekly timesheet)
- Weeks run **Sun-Sat**. Columns: Time Type, Worktags, Do Not Bill, Sun..Sat, Total, Comments.
- One row per time type. The project row looks like
  `Acme: Software Development > Project > Time Entry` (per-user: the `project` config value).
- A week that was already entered shows its rows. A **new week starts empty**: one row with Time
  Type "Select one." and all zeros.
- Fill a new week with **Auto-fill from Prior Week**. It opens a dialog: Worker, Start/End Date,
  a "Select Prior Week" dropdown (`[data-automation-id=selectWidget]`, options like
  "09/27/2026 - 10/03/2026"), a preview of the prior week's rows (Total / Time Type), and a "Do
  not copy hours" checkbox (leave it unchecked). Pick the previous week, then click OK. The grid
  now has the project row with the prior week's hours. Then fix PTO and holidays for this week.
- **Holidays**: the day's column header shows the holiday, e.g. "Mon, 9/7 (Labor Day - 2026
  Guatemala)", and that day is pre-filled with **0** on the project row. No separate holiday
  row is needed. This matches the week of Sep 6 2026 (32h total).
- **PTO**: shows as its own row with Time Type **Guatemala PTO** (8 on the PTO day), and the
  project row is 0 that day. Example: week of Aug 30 2026, Fri 9/4 = PTO 8h.
  **The assistant adds this row itself, but only for the days the user confirmed when asked
  "Any PTO or other days off this week?"** (always ask first). Click Add Row (`addRow`), open the new row's Time Type
  dropdown, choose **Guatemala PTO**, enter `hours_per_day` on each PTO day, and set the project
  row to 0 on those days. (The user confirmed this is how they do it. Approved absence requests
  are also listed under My Absence.)
- Buttons: `addRow` / `removeRow` (per row), **Save and Close**, **Save**, **Auto-fill from Prior
  Week**, and a "..." menu. Close X: `[data-automation-id=closeButton]`. Closing with changes
  prompts "Discard Changes?" (Discard / Continue).

## After Save and Close: "Enter My Time" (week calendar)
Save and Close goes to **Enter My Time**, a Sun-Sat calendar with one card per entry
("Acme: Software Development / 8 Hours - Billable / Project > Time Entry"), pay-period
markers, and a right-hand **Summary** (Project Time, Non-Billable Time, Time Off, Total Hours).
Its **Actions** menu has: Auto-fill from Prior Week, Clear, Enter Time by Type, Enter Time by
Week, Manage Absence, Quick Add, Request Absence, Review Time by Week, Run Calculations.
Clicking an empty spot in a day opens a new-entry "Enter Time" dialog. Cancel it.
Note: clicking Save with a JS `.click()` doesn't work. Use real mouse events (CDP
Input.dispatchMouseEvent).

## Save AND Submit (both required). Verified 2026-09-29.
The timesheet must end up **Submitted**, not just saved.
1. Get the user's OK on the summary.
2. In the "Enter Time by Type" grid, click **Save and Close**. You land on "Enter My Time" (the week
   calendar).
3. When the week has unsubmitted time, a **Review** button appears under the Summary panel. If the
   week is already submitted and unchanged, there is no Review button. That's expected, and
   there's nothing to submit.
4. Click **Review**. A "Submit Time" dialog opens with an attestation ("By clicking the Submit button,
   you indicate that all hours reported are true and complete..."), "Following date range will be
   submitted for approval.", e.g. "October 4 – 10, 2026 : 40 Hours", the totals (Project Time /
   Non-Billable Time / Time Off / Total Hours), an optional comment, and **Cancel / Submit**.
   Check the range and totals against the plan.
5. Click **Submit**. Confirmation: the banner **"You have submitted"** plus "Up Next: <Project
   Manager> | Time Entry: <name> - 40 hours from 10/04/2026 to 10/10/2026 for <project> - Approval
   by Project Manager", and a "View Details" button. Report success only after seeing "You have submitted".

## Absence (PTO) requests
- Home quick actions: Request Absence, Manage Absence, Time Off Balance.
- MENU > Personal > Time > My Time Off (or "My Absence") lists requests: Date, Day, Type
  ("Guatemala PTO"), Requested (8), Unit (Hours), Status (Approved).

## Known pitfalls
- Workday's date inputs ignore programmatic `.value`. Type real keystrokes.
- There can be several OK buttons in the DOM, so click the last visible one.
- Weekly Service Update: Workday is down for up to 3 hours on Fridays from 11:00 PM PDT
  (shown as the "System Status" banner).
