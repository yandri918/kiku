# Demo Script — 90 to 120 seconds

## Setup

- Three synthetic houses visible on the Today page: House 1, House 2, House 3.
- House 1: 18 days after planting (net raised, inspect_net due).
- House 2: 14 days after planting (uncover_plastic_2 and install_net due, independent).
- House 3: preparation phase (cleared, net removed, stakes pending).

## Steps

### Step 1 — Today view (10s)
Open the app. Show the Today page with scheduled tasks for all three houses.
Point out that cutting and packing appear alongside field tasks.

### Step 2 — Enter a note for House 3 (20s)
Navigate to Journal. Set working date to today. Enter:

  "House 3 cleared, net removed, stakes not yet done."

Click "Extract Draft". Wait for the model response.

### Step 3 — Review the draft (20s)
Show the draft panel:
- Three events with status badges (done, done, not_done).
- Each event shows its source evidence quote in italics.
- Clarification: "Please confirm the working date."

Click "Save Approved Events". Confirm the save.

### Step 4 — House 2 at 14 days (15s)
Return to Today. Show that House 2 has two separate tasks:
- Uncover plastic (after planting) — 14 DAP.
- Install net — 14 DAP.
Emphasize these have independent status; completing one does not complete the other.

### Step 5 — Net raise and inspection (20s)
Back in Journal. Enter:

  "Net on House 2 has been raised. House 1 check tomorrow."

Show the draft: raise_net for House 2 (done), inspect_net for House 1 (planned).
Approve.

### Step 6 — Agenda view (10s)
Navigate to Agenda. Show packing schedule (Tue/Thu/Sun) alongside cutting dates.
Confirm packing has not shifted after any changes.

### Step 7 — Evaluation page (20s)
Navigate to Evaluation. Show the metrics table with baseline and fine-tuned scores.
Show one example where fine-tuned correctly disambiguates "opened" with cycle context.
Show one error example from the baseline.
Confirm scores come from the full locked test set.

### Step 8 — Close (5s)
Show the Render deployment URL in the browser address bar.
Mention that training was run on Tinker (show the checkpoint ID or run record).

## Notes

- All data shown is synthetic and labeled.
- Overall scores are from the full 100-example test set, not cherry-picked.
- Demo write access is rate-limited.
