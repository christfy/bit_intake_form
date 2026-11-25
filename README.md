# BiT Intake & Review check-in

A page Richard uses with Build in Tulsa staff to confirm, program by program, how people get picked: how they get in, the review steps, what rules someone out, and what happens after selection. Each confirmation lands in a Google Sheet, ready to turn into the data dictionaries.

## What's in the folder

| Path | What it is |
| --- | --- |
| `public/index.html` | The whole page (HTML, CSS and JS in one file). |
| `api/programs.js` | `GET /api/programs`: checks the passcode, returns the drafts plus the latest saved answers from the sheet. |
| `api/submit.js` | `POST /api/submit`: checks the passcode, validates, forwards to the sheet. |
| `api/_lib.js` | Shared helpers (not a route). |
| `data/programs.json` | The "here's what we think" drafts. Not public: only the API serves it, behind the passcode. |
| `google-apps-script/Code.gs` | The script that writes to the Google Sheet. |
| `tools/build_programs.py` | Source of the drafts. Edit this, then run it to rebuild `data/programs.json`. |
| `tools/dev-server.js` | Local test server with a fake sheet that runs the real `Code.gs`. |
| `tools/build-preview.js` | Builds a one-file offline preview with the drafts embedded. |

## Deploy (about 15 minutes)

### 1. Google Sheet

1. Create a Google Sheet, for example "BiT Intake & Review responses", in a shared team drive.
2. Open Extensions > Apps Script. Replace `Code.gs` with `google-apps-script/Code.gs`.
3. Change `SECRET` at the top to a long random string. Keep it; Vercel needs the same value.
4. Deploy > New deployment > type **Web app**. Execute as: **Me**. Who has access: **Anyone**. Authorize when asked.
   "Anyone" lets Vercel's server reach it. The secret is what keeps everyone else out.
5. Copy the web app URL (ends in `/exec`).

### 2. Vercel

1. Put this folder in a GitHub repo and import it in Vercel, or run `npx vercel` from inside the folder.
2. Framework preset: **Other**. Leave the build command empty. `vercel.json` already sets the output folder to `public`.
3. Settings > Environment Variables (Production), then redeploy:

| Name | Value |
| --- | --- |
| `ACCESS_CODE` | The passcode you'll give Richard. |
| `SHEET_WEBHOOK_URL` | The Apps Script `/exec` URL. |
| `SHEET_SECRET` | The same `SECRET` as in `Code.gs`. |

### 3. Check it

Open the Vercel URL, enter the passcode, open any program and press **Save progress**. A row should appear in the sheet's **Responses** tab. Delete that test row.
If the home page says "Saving to: This device (sheet not connected)", one of the two sheet variables is missing or wrong.

## Running it locally

```
node tools/dev-server.js          # http://localhost:3100, passcode: test-code, fake sheet
NO_SHEET=1 node tools/dev-server.js 3101   # same, with the sheet switched off
```

Node 18 or newer. No packages to install.

## Changing the drafts

Edit `tools/build_programs.py`, run `python3 tools/build_programs.py`, and redeploy. Bump `version` at the bottom of that file when you do, so people can see which drafts they confirmed against. Every value carries a confidence (`doc`, `guess` or `unknown`) and the source ids it came from.

## How the page behaves

- **Solid underline** means BiT's own documents say it. **Dashed** is our guess. **"?"** means nothing was written down. Green check means someone confirmed it.
- **Session notes** (top right) shows Richard what to ask at each part. **Team view** shows the model terms: stage types, the status roll-up, rubrics, workflow pattern and flags. Keep both off while sharing the screen, unless notes help.
- Edits are kept in the browser as you go, and **Save progress** or **Confirm** sends them to the sheet. A different laptop sees the latest saved version.
- The passcode is shared. Change `ACCESS_CODE` in Vercel to rotate it.

## Turning confirmations into data dictionaries

Every row's JSON payload carries `model`, a program's intake and review mapped onto the W.E. Build model: the Program Workflow row, the workflow and its stages (stage type, status shown, rubric type and criteria, reviewers, decisions), the knock-out rules, the application status path, post-selection steps for the participation phase, and the answered questions. The same JSON is in Team view under **Copy data dictionary JSON**.

## Conventions this build uses (change in `public/index.html`, the `KINDS`, `JUDGE` and `OUT` lists)

- Stage decisions: Advance, Hold, Waitlist, Decline. These were not settled as of Nov 19.
- Status names use the "-ing" form where it reads naturally: Screening, Interviewing. "Committee Review" is flagged because it has no natural "-ing" form.
- A knock-out run automatically at submission is not a numbered step (W.E. Build). A knock-out done by hand is shown as an "Eligibility check" step, stage type Knock-out.
- Pitch Night judging and prizes sit under "After someone is picked", because they belong to participation, not intake.
