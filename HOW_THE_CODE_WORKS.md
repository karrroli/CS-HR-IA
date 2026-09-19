# How the code works (plain-language guide)

This guide explains every part of the Candidate Matcher so it can be explained to a teacher. It is written to be read next to `app.py`.

## 1. The big picture

The program is a small website. It has two pages and one database file.

| Part | File | What it is for |
|------|------|----------------|
| Program logic | `app.py` | Everything the program does: login, upload, keywords, scoring, sorting |
| Login page | `templates/login.html` | Email and password form |
| Dashboard page | `templates/dashboard.html` | Upload section, keyword section, results section |
| Appearance | `static/style.css` | Colours, table borders, the green top-three rows |
| Database | `matcher.db` | Created automatically on first run, holds all the data |

When the user clicks a button, the browser sends a form to the program. The program does its job, saves to the database, and sends the user back to the dashboard, which is re-drawn from the database. There is no JavaScript at all — every change is "click, reload, see the result".

```
Login page --> Dashboard --> Upload files  ----\
                         --> Add/Save/Delete keyword ---> back to Dashboard
                         --> Process  --> score each resume --> bubble sort --> leaderboard
```

## 2. The database (Criterion C ERD)

Four tables, exactly the ones in the ERD:

- **User** — `user_id`, `email`, `password_hash`
- **Candidate** — `cand_id`, `user_id`, `name`, `contact`, `resume_text`
- **Job** — `job_id`, `user_id`, `keyword1` … `keyword5`
- **Match** — `match_id`, `cand_id`, `job_id`, `match_score`

`init_db()` creates the tables with `CREATE TABLE IF NOT EXISTS`, then adds the HR account (`hr@gmail.com` / `hr12345`) and one empty job for that user. Because of `IF NOT EXISTS`, running the program again does not damage existing data.

The password is never stored as plain text. `generate_password_hash` turns it into a long scrambled string (a hash). At login, `check_password_hash` compares the typed password with that hash.

`get_db()` opens the database file. Every function that needs the database follows the same three steps: **open, ask, close**. This pattern comes from the official Flask tutorial.

## 3. Login (SC-01, Flowchart 1)

Function: `login()`

1. If the page is only being shown (GET), display the form.
2. If the form was sent (POST), read the email and password.
3. If either is empty, show "Please enter both email and password." and stay on the page. (T-03)
4. Look up the email in the User table.
5. If the user is not found, or the password does not match the hash, show "Invalid email or password." and stay. (T-02)
6. Otherwise remember `user_id` in the **session** (Flask's way to remember who is logged in) and go to the dashboard. (T-01)

`is_logged_in()` simply checks whether `user_id` is in the session. Every dashboard action starts with "if not logged in, go to the login page", so nobody can reach the dashboard by typing the address directly.

`logout()` clears the session.

## 4. Upload (SC-02, SC-08, Flowchart 2)

Function: `upload()`

1. Get the list of files from the form. `<input type="file" multiple>` on the page lets the user select many files at once — 10 or more is fine. (T-07)
2. If nothing was selected, show "No file selected." (T-06)
3. For every file:
   - If the name does not end in `.txt`, show a rejection message and skip it. (T-05)
   - Read the text. If the file is empty, reject it.
   - The **name** is the first line of the file.
   - The **contact** is found by `find_contact()`: the first word that contains `@`.
   - `save_candidate()` stores the name, contact and full text in the Candidate table. (T-04)
4. Show how many files were saved.

Reading the file is inside `try / except`, so a broken file produces a message instead of a crash (this is the "file upload" try-except from Criterion B).

**Replace, not duplicate.** If a candidate with the same name already exists for this HR user, `save_candidate()` updates the old record and clears its old score instead of adding a second copy. This keeps the list clean when the same file is uploaded twice during testing.

## 5. Keywords (SC-03, SC-04, Flowchart 3)

The Job table has five fixed slots: `keyword1` to `keyword5`. An empty slot holds an empty string `""`.

- `get_keyword_list(job)` walks through slots 1 to 5 and collects the ones that are not empty into a normal Python list.
- `set_keyword_slot(job, slot, keyword)` writes a value into one slot (writing `""` empties it).
- `keyword_exists(job, keyword)` checks for a repeat, ignoring capital letters.

Buttons:

- **Add keyword** → `add_keyword()`: rejects an empty keyword, a repeated keyword, or a sixth keyword; otherwise puts the word into the first empty slot. (T-08)
- **Save** (next to a keyword) → `edit_keyword()`: changes the text in that slot. (T-09)
- **Delete** → `delete_keyword()`: empties that slot. (T-09)

Because the dashboard is always drawn from the database, the keyword list is still there after refreshing the browser. (T-10)

## 6. Scoring — linear search (SC-05, Flowchart 5)

Functions: `clean_words()` and `get_score()`

`clean_words(text)` makes the text lower-case and replaces every character that is not a letter or digit with a space, then splits it into a list of words. So `"Python, Flask."` becomes `["python", "flask"]`. This is why "Python" and "python," count as the same word.

`get_score(resume_text, keyword_list)` is the linear search from the flowchart:

```
score = 0
for every word in the resume:
    for every keyword:
        if the word equals the keyword:
            score = score + 1
```

Every occurrence counts. A resume that mentions "Python" four times gets 4 points for that keyword. This is what Criterion A describes. (It is also a fair limitation to discuss in Criterion E — a candidate could repeat a word many times to get a high score.)

Keywords are compared as single words. A keyword with a space in it, such as `Flask framework`, can be added to the list but will never equal a single word, so it scores 0. In practice keywords should be single words like `Flask`.

## 7. Process button (SC-05)

Function: `process()`

1. Read the keyword list and all candidates of this user.
2. If there are no candidates, show a message and do nothing else — the program does not crash. (T-12)
3. If there are no keywords, show a message too.
4. Otherwise delete the old scores for this job, then for every candidate compute `get_score()` and insert a row in the Match table.

The database work is inside `try / except sqlite3.Error` — this is the "database" try-except from Criterion B.

## 8. Leaderboard — bubble sort (SC-06, SC-07, Flowchart 4)

Functions: `dashboard()` and `bubble_sort()`

When the dashboard is drawn, it reads all candidates and, for each one, looks up its score in the Match table. Each candidate becomes a small list: `[cand_id, name, contact, score]`. Candidates without a score go into a separate "Not scored yet" list (they were uploaded after the last Process).

`bubble_sort(candidate_list)` sorts the scored list from highest to lowest:

```
for i from 0 to n-2:
    for j from 0 to n-2-i:
        if the score at position j is lower than the score at position j+1:
            swap them
```

After each pass of the inner loop the lowest remaining score has "bubbled" to the end. Candidates with equal scores keep their upload order. Python's built-in `sort()` is deliberately not used, so the sorting is visible in the code.

On the page, `loop.index` gives the rank (1, 2, 3 …). Ranks 1–3 get the CSS class `top-three`, which colours the row green. (T-13, T-14, T-15)

The leaderboard is drawn from the Match table every time, so scores are still shown after a refresh or after logging out and back in. (T-16)

## 9. Where the code differs from the Criterion B / C text

These are small and worth fixing in the write-up so everything matches:

| In the report | In the code | Why |
|---------------|-------------|-----|
| `flask_login` / `@login_required` | Flask's own `session` and an `is_logged_in()` check | Same idea, fewer moving parts to explain |
| Bootstrap | plain `style.css` | Nothing to explain that is not visible in the file |
| Table called "Requirements" in one place, "Job" in the ERD | `Job` | The ERD is the authoritative design |
| "Final score is stored in Candidate table" (one line in B) | Stored in `Match`, as the ERD shows | The ERD is the authoritative design |
| Test environment lists the password as `wrong123` | Real password is `hr12345`; `wrong123` is the wrong password in T-02 | The two lines in the report disagree with each other |
| Buttons: Upload, Add keyword, Delete, Process | Also **Save** (edit keyword), **Remove** (candidate), **Logout** | Save is needed for "edit"; Remove is needed to run T-12 after an upload; Logout is needed for T-16 |
| "Contact details extracted" | The first word containing `@` | Simplest rule that works for LinkedIn text |

## 10. Sources to cite

- **Flask tutorial ("Flaskr")** — the template for the overall structure: one Python file, SQLite opened per request, login stored in the session, password hashing, HTML templates.
  https://flask.palletsprojects.com/en/stable/tutorial/
- **Flask file upload pattern** — `request.files`, checking the file extension.
  https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
- **Flask message flashing** — the `flash()` messages shown at the top of each page.
  https://flask.palletsprojects.com/en/stable/patterns/flashing/
- **Werkzeug security** — `generate_password_hash` and `check_password_hash`.
  https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security
- **Python sqlite3 module** — `connect`, `execute`, `fetchone`, `fetchall`, `commit`.
  https://docs.python.org/3/library/sqlite3.html
- The **linear search** and **bubble sort** follow the flowcharts in Criterion C of this IA. They were not copied from a repository.

### About AI assistance

The first draft of these files was produced with the help of an AI coding assistant, working from the design in Criteria A–C. The IB requires this to be acknowledged. Recommended steps before submission:

1. Retype the program by hand rather than copying the files, so every line has been written by you at least once.
2. Rename variables and rewrite the comments in your own words.
3. Add one acknowledgement sentence to the bibliography, for example: *"An AI coding assistant was used to draft parts of the program from my Criterion B/C design; the structure follows the official Flask tutorial (cited above). All code was reviewed, retyped and adapted by me."*
4. Make sure you can explain every function in this guide without reading it.

## 11. Quick test walk-through

1. Log in with `hr@gmail.com` / `hr12345`.
2. Upload all 12 files from `sample_cvs/` in one go.
3. Add keywords `Python`, `Flask`, `SQL`, `Communication`, `Teamwork`. Try to add a sixth — it is refused.
4. Click **Process**. Karolina, Daniel and Lucas should be at the top in green; Sofia Rossi should be last with 0.
5. Change `Flask` to `Django`, click Save, click Process again — Daniel Kim's score changes.
6. Try `sample_cvs/bad_files/resume.pdf` and `empty.txt` — both are rejected with a message.
7. Remove all candidates and click Process — the "No candidates" message appears.
