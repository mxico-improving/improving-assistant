# Engage screen map (engage.improving.com)

Status: MAPPED 2026-09-29 (Engage API v11.4.0, Client v10.5.0). Read-only session; nothing was submitted.
Update this file when the UI changes.

## Access
- URL: https://engage.improving.com. It sits behind a Cloudflare bot check, and headless or automated
  browsers get stuck on "Just a moment...". Use a normal, visible Chrome window.
- Microsoft SSO with an Improving account. The user approves MFA.
- Home: /app/main/dashboard/employee-home. The left sidebar has "EIP Points > Record Activity".

## "Add Activity" form
Page: https://engage.improving.com/app/main/involvement/activity (Involvement > Activity)

| Field | Element | Notes |
|---|---|---|
| Activity Category | `select[name=QuickAddActivityCategory]` | first option "Select a category..." |
| Activity Type | `select[name=QuickAddActivityDefinition]` | repopulates after the category `change` event |
| Date | `#Activity_OccuranceDate` | text, MM/DD/YYYY, bsDatepicker, defaults to today |
| Quantity | `#Activity_Quantity` | number, default 1 |
| Notes | `#Activity_Notes` (textarea) | free text |
| Submit | button "Add N points" | N = points for the selected type x quantity; "Add 0 points" when nothing is selected |

Below the form, "Current Activities" lists the quarter's entries (Category, Type, Date, Quantity,
Points, Notes, Creation time) with Edit / Delete / Share. The "Reporting Period" select at the
top filters by quarter (e.g. 2026-Q3).

## Weekly "full week" activity
- Category: **Direct Revenue**. Type: **40 Billable Hour Week** (5 points).
- Only when every weekday is worked (no PTO, no holiday). Otherwise skip it.
- Convention (from existing entries): Date = the Friday of the week. Notes = the week range, e.g.
  "September 21 - 25" (format "<Month> <Mon day> - <Fri day>"; if the week spans two months,
  write e.g. "September 28 - October 2").
- Before adding, check "Current Activities" for an existing 40 Billable Hour Week entry dated
  in the same week, to avoid duplicates.
- Related types in the same category (don't use them for this): "OVER 40 Billable Hour Week" (1),
  "Required Support - 8pm-6am" (1), "Required Support - Weekend" (1).

## Categories, types and points
Points are per unit of quantity, as shown on the "Add N points" button with quantity 1.

| Category | Type | Points |
|---|---|---|
| Account Management | Azure Partner Admin Link | 15 |
| Account Management | Consulting Contract <=$10K | 10 |
| Account Management | Consulting Contract >$100K | 90 |
| Account Management | Consulting Contract >$10K and <=$100K | 60 |
| Account Management | Consulting/Training/Placement Lead - Prospect | 15 |
| Account Management | Participation in Bluesheet Creation | 15 |
| Account Management | Placement Contract | 30 |
| Account Management | Qualified Consulting Lead | 15 |
| Account Management | Qualified Contact | 3 |
| Account Management | Training Contract | 15 |
| Business Development | Consulting - Prospect | 12 |
| Business Development | Consulting Contract <=$10K | 30 |
| Business Development | Consulting Contract >$100K | 150 |
| Business Development | Consulting Contract >$10K and <=$100K | 60 |
| Business Development | Placement Contract | 75 |
| Business Development | Placement Prospect | 6 |
| Business Development | Qualified Consulting lead | 60 |
| Business Development | Qualified Contact | 6 |
| Business Development | Qualified Placement Lead | 30 |
| Business Development | Training Contract | 30 |
| Business Development | Training Prospect | 6 |
| Certification/Recognition | Microsoft Certification | 15 |
| Certification/Recognition | Microsoft MVP | 50 |
| Certification/Recognition | Other Certification | 15 |
| Certification/Recognition | Scrum.org (PST, Trainer) | 75 |
| Come Together | Challenge Participation | 10 |
| Come Together | In-Person Attendance | 10 |
| Come Together | Virtual Attendance | 3 |
| Direct Revenue | 40 Billable Hour Week | 5 |
| Direct Revenue | OVER 40 Billable Hour Week | 1 |
| Direct Revenue | Required Support - 8pm-6am | 1 |
| Direct Revenue | Required Support - Weekend | 1 |
| Education/Coaching | Adjunct Instructor | 2 |
| Education/Coaching | Client Brown Bag | 2 |
| Education/Coaching | ImprovingU Attendance | 1 |
| Education/Coaching | ImprovingU Course Preparation | 1 |
| Education/Coaching | ImprovingU Group Discussion | 1 |
| Education/Coaching | ImprovingU Group Discussion Facilitation | 2 |
| Education/Coaching | ImprovingU Instructor Delivery | 5 |
| Education/Coaching | ImprovingU Key Course Attendance | 2 |
| Education/Coaching | ImprovingU Key Course Instructor Delivery | 6 |
| Education/Coaching | ImprovingU Key Course Student Work | 1 |
| Education/Coaching | ImprovingU Planning | 2 |
| Education/Coaching | ImprovingU Remote Facilitation | 3 |
| Education/Coaching | Personal Coaching | 3 |
| Education/Coaching | Project Review Presentation | 3 |
| Improving Cares | Community Service | 1 |
| Improving Path | Active Commitment | 3 |
| Improving Path | Meeting | 1 |
| Improving Path | Professional Development Coaching | 3 |
| Industry Contribution/Leadership | Board Participation | 20 |
| Industry Contribution/Leadership | Lead User Group | 10 |
| Industry Contribution/Leadership | Open Source or Internal Development | 4 |
| Industry Contribution/Leadership | Presentation - Conference | 60 |
| Industry Contribution/Leadership | Presentation - Improving Talks | 20 |
| Industry Contribution/Leadership | Presentation - Lightning Talk | 10 |
| Industry Contribution/Leadership | Presentation - Major | 120 |
| Industry Contribution/Leadership | Presentation - User Group | 20 |
| Industry Contribution/Leadership | Publication - Major | 40 |
| Industry Contribution/Leadership | Publication - Minor | 20 |
| Industry Participation | Conference - Business Day | 0 |
| Industry Participation | Conference - Vacation Day | 6 |
| Industry Participation | Conference - Weekend | 3 |
| Industry Participation | Podcast Contribution | 5 |
| Industry Participation | Podcast Production | 10 |
| Industry Participation | Relevant Blog Post | 3 |
| Industry Participation | Relevant Social Media Posts | 2 |
| Industry Participation | User/Professional Group Attendance | 1 |
| Merger/Acquisition | Letter of Intent/Terms Sheet | 45 |
| Merger/Acquisition | Letter of Interest | 30 |
| Merger/Acquisition | Qualified Lead | 15 |
| Networking | Improving Event Attendance | 1 |
| Networking | Improving Event Host | 4 |
| Networking | Improving Event Planning | 2 |
| Networking | Meeting | 1 |
| Networking | Partner Event | 1 |
| Operations Support | Corporate Initiative Meeting | 2 |
| Operations Support | Lead Corporate Initiative | 10 |
| Operations Support | Maintain Business Report | 5 |
| Operations Support | Maintain KPI Report | 5 |
| Operations Support | Website Development | 1 |
| Operations Support | Weekend Support | 1 |
| Other | Miscellaneous | 1 |
| Recruiting | Interview - In Person | 8 |
| Recruiting | Interview - Phone | 4 |
| Recruiting | Referral - Hire | 100 |
| Recruiting | Referral - NonHire | 10 |
| Sales/Marketing Support | Case Study Creation - Interviewee | 15 |
| Sales/Marketing Support | Case Study Creation - Interviewer | 25 |
| Sales/Marketing Support | Create News Item | 5 |
| Sales/Marketing Support | Create Produced Collateral | 2 |
| Sales/Marketing Support | Create Webpage Content | 2 |
| Sales/Marketing Support | Email Campaign | 1 |
| Sales/Marketing Support | Proposal - Large | 50 |
| Sales/Marketing Support | Proposal - Small | 25 |
| Sales/Marketing Support | Support Proposal (estimation) | 12 |
| Sales/Marketing Support | Support Sales Meeting | 20 |
| Sales/Marketing Support | User Group Host | 20 |
| Sales/Marketing Support | User Group Referral - Large (20+ people) | 15 |
| Sales/Marketing Support | User Group Referral - Other | 5 |
| User Experience | (no types available) | |

## Confirmation
- TODO: confirm on the first real submission. We expect a new row to appear at the top of
  "Current Activities". Verify the row (type, date, notes) before reporting success.
