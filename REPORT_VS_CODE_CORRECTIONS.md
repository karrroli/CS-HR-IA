# Report vs program — discrepancies and ready-to-paste fixes

This file compares the written IA report with what the program actually does.  
**Do not change the program.** Copy the “Use this wording instead” sentences into your report.

Source checked for Criterion A: Google Drive file [Karolina Criteria A..docx](https://drive.google.com/file/d/1p2i55yMLrJ8F3yGfYepL337oDM1ANCMv/view).  
Criteria B and C were not found as separate files on Drive; those rows use the known differences already listed in `HOW_THE_CODE_WORKS.md`.

---

## Summary

| Status | Count |
|--------|------:|
| Matches the program | 6 |
| Needs a wording fix in the report | 9 |
| B/C text not found on Drive — fix when you open that draft | 7 |

---

## Criterion A — what already matches

These lines in Criteria A are fine. Leave them.

| Report idea | What the program does |
|-------------|------------------------|
| Web app; HR uploads LinkedIn text as `.txt` | Dashboard upload accepts `.txt` files |
| Linear search; score +1 per keyword hit | `get_score` nested loops count every match |
| Bubble sort; highest to lowest | `bubble_sort` on the dashboard |
| Login with email and password | `hr@gmail.com` / `hr12345` |
| Match score shown next to each candidate | Leaderboard column “Match score” |
| Top three on the leaderboard | Green `top-three` rows |
| 10+ file uploads | `multiple` on the file input; sample set has 12 files |

---

## Criterion A — fix these wording lines

### 1. Job “requirements” examples are wrong

**In the report now:**  
“Program allows to fill in job requirements (e.g. years of experience, relevant education etc.)”

**What the program does:**  
Up to five single-word skill keywords (for example `Python`, `Flask`, `SQL`). It does not store years of experience or education level as separate fields.

**Use this wording instead:**  
“Program allows the HR user to enter up to five job requirement keywords (for example skill words such as Python, Flask or SQL).”

---

### 2. “Contact details” is too vague

**In the report now:**  
“HR can upload a .txt file with the information of the candidate from LinkedIn (e.g. name, contact details etc.)”

**What the program does:**  
Name = first line of the file. Contact = first word that contains `@` (an email). Phone numbers are not extracted.

**Use this wording instead:**  
“HR can upload one or more .txt files exported from LinkedIn. The program stores the candidate’s name (first line of the file) and contact email (the first word containing @), together with the full resume text.”

---

### 3. Computational context should name Flask and SQLite

**In the report now:**  
Only Python and `.txt` files are mentioned.

**What the program does:**  
A Flask website with HTML templates, a CSS file, and a SQLite database file `matcher.db`.

**Use this wording instead (add after the Python sentence):**  
“The website is built with Flask. Data is stored in a SQLite database file. The pages are HTML templates with a simple CSS stylesheet. There is no JavaScript.”

---

### 4. Success criteria should mention the five-keyword limit

**Missing from Criteria A, but true in the program:**  
A sixth keyword is refused. Empty and duplicate keywords are refused.

**Add this success criterion:**  
“HR can add, edit and delete job keywords, with a maximum of five keywords at a time; empty and duplicate keywords are rejected.”

(This replaces the vague “Requirements can be changed, added or deleted…” line, or sit next to it.)

---

### 5. Success criteria should mention rejected bad files

**Missing from Criteria A, but true in the program:**  
Non-`.txt` files and empty files are rejected with a message; other selected files still upload.

**Add this success criterion:**  
“The program rejects files that are not .txt or that are empty, shows a clear message, and continues with any valid files selected in the same upload.”

---

### 6. “Immediately shown” — clarify how

**In the report now:**  
“Requirements can be changed, added or deleted by an HR and changes are immediately shown in the system”

**What the program does:**  
After Add / Save / Delete, the browser returns to the dashboard and the page is redrawn from the database. There is no live update without a reload. That is still “shown in the system” after each action.

**Use this wording instead:**  
“Keywords can be added, edited or deleted. After each action the dashboard reloads from the database so the updated keyword list is shown.”

---

## Ready-to-paste Criterion A success criteria (full list)

Replace your current bullet list with this, so A matches the finished program:

1. Program allows HR to log in using an email and password.  
2. HR can upload one or more LinkedIn `.txt` files; name is taken from the first line and contact email from the first word containing `@`.  
3. HR can enter up to five job requirement keywords (single skill words).  
4. Keywords can be added, edited or deleted; empty words, duplicates and a sixth keyword are rejected; the list reloads from the database after each change.  
5. After Process, a match score is shown next to each scored candidate.  
6. Candidates are sorted from highest to lowest match score using bubble sort.  
7. The final leaderboard highlights the top three candidates.  
8. The program handles 10 or more `.txt` uploads in one selection.  
9. Non-`.txt` and empty files are rejected with a message without stopping the other uploads.  
10. If Process is pressed with no candidates or no keywords, a message is shown and the program does not crash.

---

## Criteria B / C — fix these when you open that draft

These files were not found on Google Drive under this account. Use this checklist against your Criterion B and C text (and against section 9 of `HOW_THE_CODE_WORKS.md`).

| # | If the report says… | Change it to match the program… | Ready wording |
|---|---------------------|----------------------------------|---------------|
| B1 | `flask_login` / `@login_required` | Flask `session` and `is_logged_in()` | “Login is remembered with Flask’s session. Each protected page checks `is_logged_in()` and sends the user back to login if needed.” |
| B2 | Bootstrap | Plain `static/style.css` | “The pages use a simple CSS file. Bootstrap is not used.” |
| B3 | Table named “Requirements” | Table named `Job` | “Job requirements are stored in the Job table as keyword1 to keyword5.” |
| B4 | “Final score is stored in the Candidate table” | Score is in the `Match` table | “Each score is stored in the Match table as match_score, linked to cand_id and job_id.” |
| B5 | Test password listed as `wrong123` | Real login password is `hr12345`; `wrong123` is only the wrong password in test T-02 | “Test login: email `hr@gmail.com`, password `hr12345`. Test T-02 uses the wrong password `wrong123`.” |
| B6 | Buttons only: Upload, Add keyword, Delete, Process | Also Save, Remove, Logout | “Dashboard actions: Upload, Add keyword, Save, Delete keyword, Process, Remove candidate, Logout.” |
| B7 | “Contact details extracted” (vague) | First word containing `@` | “Contact is the first word in the resume that contains the @ character; if none is found, the program stores ‘not found’.” |

---

## Extra facts that are true in the program (optional to add in B/C/D)

Use these if a paragraph still sounds like an older design:

- One HR account is created automatically: `hr@gmail.com` / `hr12345`.  
- Passwords are stored as a hash, not as plain text.  
- Uploading the same candidate name again replaces the old resume and clears the old score.  
- Process deletes old Match rows for that job, then inserts one new score per candidate.  
- Candidates uploaded after the last Process appear under “Not scored yet” until Process is clicked again.  
- Scores remain after refresh or logout/login, because they are in the Match table.  
- Sorting happens when the dashboard is drawn, not inside the Process button itself.

---

## What you should do next in Google Drive

1. Open [Karolina Criteria A..docx](https://drive.google.com/file/d/1p2i55yMLrJ8F3yGfYepL337oDM1ANCMv/view).  
2. Paste the **Ready-to-paste Criterion A success criteria** list above.  
3. Soften the job-requirements examples (no “years of experience” / “education” as separate fields).  
4. Add the Flask + SQLite sentence to Computational Context.  
5. Open your Criterion B and C draft (wherever you keep it) and apply the B1–B7 table.  
6. If you share the B/C file link here, the same check can be done line by line on that text.
