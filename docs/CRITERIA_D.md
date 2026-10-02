# Criterion D – Development

This section shows the main techniques used to build the Candidate Matcher. For each technique I include a short code excerpt, explain what it does, justify why I chose it, and explain how it links to the Criterion A success criteria. Full source code is in **Appendix A** (`APPENDIX_SOURCE_CODE.txt`). Line numbers below match that file. The appendix is comment-free. Code screenshots show the same pure code with no comments.

---

## 1. Password hashing and login

![Login / password hashing code excerpt](criteria_d/screenshots/code_01_login_hash.png)

*See Appendix A, lines 39–40 and 134–138.*

The first technique hashes the HR password before it is stored in SQLite, and checks it again at login. `generate_password_hash()` turns `"hr12345"` into a long scrambled string, so the real password is never saved as plain text. At login, `check_password_hash()` compares the typed password with the stored hash. If the email is missing or the password is wrong, an error is shown and the user stays on the login page. If the match is successful, `session["user_id"]` remembers who is logged in.

I chose password hashing instead of storing the password in plain text because login data is sensitive. Even if somebody opened the SQLite file, they would only see the hash. Flask sessions are also better than sending the password on every page, because only the user id is kept after a successful login.

**Link to success criteria:** This technique implements **SC-01** — *the program allows HR to log in using an email and password*. Without a working login check, SC-01 fails. The hash-and-check path is what accepts a correct login (T-01) and rejects a wrong password (T-02). Empty fields are blocked before the hash check (T-03), so the same criterion is covered for both valid and invalid login data.

---

## 2. File reading and upload validation

![File upload validation code excerpt](criteria_d/screenshots/code_02_file_upload.png)

*See Appendix A, lines 190–205.*

This excerpt shows how LinkedIn text enters the system. `request.files.getlist("files")` receives one or many files in one submission. The code checks that a file was selected, then that each name ends with `.txt`. Invalid types are rejected with a flash message and are not stored. Empty files are also rejected. For a valid file, `.read()` loads the text and the candidate name is taken from the first line.

I chose simple `.txt` files rather than PDF or a LinkedIn API because Python can process them with basic string methods, and my client can copy profile text without complex formatting. Checking the extension before saving stops wrong files from entering the Candidate table. Using `getlist()` also allows 10 or more files at once.

**Link to success criteria:** This technique implements **SC-02** — *HR can upload LinkedIn `.txt` files and the name is taken from the first line* — and **SC-08** — *the program handles 10 or more `.txt` uploads in one selection*. The `getlist("files")` loop is what makes multi-file upload possible (T-07). The `.txt` check and empty-file check protect SC-02 by rejecting bad input (T-05, T-06) while still accepting a valid file (T-04).

---

## 3. Linear search for match scoring

![Linear search scoring code excerpt](criteria_d/screenshots/code_03_linear_search.png)

*See Appendix A, lines 90–97.*

`get_score()` is the matching algorithm from Flowchart_5. First `clean_words()` turns the resume into lower-case words and removes punctuation, so `"Python,"` and `"python"` match. Then a nested loop compares every resume word with every keyword. Each equal pair adds 1 to the score. The final score is stored in the Match table and shown next to the candidate name.

I chose linear search because the resume text is not sorted, so binary search cannot be used. Linear search is simple to implement and explain, and it matches the plan in Criterion A. For a few hundred resume words and only five keywords, O(n × m) is fast enough for about 10–50 candidates. A NLP library could give smarter matches, but it would hide the algorithm.

**Link to success criteria:** This technique implements **SC-05** — *after Process, a match score is shown next to each scored candidate*. The nested linear search is what produces that score. Without `get_score()`, Process would have nothing meaningful to save or display. T-11 confirms scores appear for all candidates; a zero-score case (Sofia Rossi scored 0) still satisfies SC-05 because a score is shown even when no keyword hits.

---

## 4. Bubble sort for the leaderboard

![Bubble sort ranking code excerpt](criteria_d/screenshots/code_04_bubble_sort.png)

*See Appendix A, lines 99–108.*

After scoring, `bubble_sort()` ranks candidates. Nested loops compare neighbours and swap them if the left score (`left[3]`) is lower than the right score, so the list ends highest to lowest. The dashboard shows this list and highlights the first three rows in green with the `top-three` CSS class.

I chose bubble sort because the list is small (about 10–50 people), so O(n²) is acceptable, and it sorts in place with almost no extra memory. That fits better here than merge sort, which needs extra arrays. Python’s built-in `sorted()` would be shorter, but I wrote bubble sort myself so the ranking algorithm is visible.

**Link to success criteria:** This technique implements **SC-06** — *candidates are sorted from highest to lowest match score using bubble sort* — and **SC-07** — *the final leaderboard highlights the top three candidates*. Bubble sort is the direct fulfilment of SC-06 (T-13). Once the list is ordered, ranks 1–3 can be highlighted, which fulfils SC-07 (T-14, T-15). If sorting were wrong, the green top-three highlight would mark the wrong people, so both criteria depend on this technique.

![Sorted leaderboard with top three highlighted](criteria_d/screenshots/test_T14_leaderboard.png)

*Figure: Observed leaderboard after Process (T-13, T-14, T-15). Top three rows are green; scores go from 17 down to 0 — evidence for SC-06 and SC-07.*

---

## 5. SQLite parameterised queries

![SQLite parameterised query code excerpt](criteria_d/screenshots/code_05_sqlite.png)

*See Appendix A, lines 309–314.*

When Process is clicked, old Match rows for the job are deleted, then each score is inserted with a parameterised SQL statement. The `?` placeholders are filled with `cand_id`, `job_id` and `match_score`. `db.commit()` saves the changes so scores remain after the browser is closed.

I chose SQLite with `?` parameters instead of building SQL with `+` because parameters are safer and clearer. SQLite is a single file, needs no separate server, and matches the Criterion C design. A limitation is that SQLite is not ideal for many users at once, but this product is for one HR client.

**Link to success criteria:** This technique supports **SC-05** and **SC-07** by making scores persistent. SC-05 requires a score next to each candidate; SC-07 requires a leaderboard of those scores. Saving each result in the Match table with `?` parameters is how the program keeps name-and-score data after Process, refresh, or logout/login. Without these inserts and `commit()`, the leaderboard would be empty and both criteria would fail in normal use (T-11, T-14).

---

## 6. Error handling for invalid data

![Error handling code excerpt](criteria_d/screenshots/code_06_error_handling.png)

*See Appendix A, lines 126–128 and 303–306.*

Error handling is used across login, upload, keywords and Process. Empty fields, wrong passwords, non-`.txt` files, empty or duplicate keywords, and Process with missing data all show a flash message instead of crashing. File reading is also in `try/except` so a broken file does not stop the whole upload loop.

I chose flash messages with early `return` / `continue` because they keep the HR on a familiar page and explain what went wrong. This is more useful than a Python traceback and makes the Criterion C negative tests possible.

**Link to success criteria:** Error handling protects several criteria when input is invalid:
- **SC-01** — empty or wrong login must not open the dashboard (T-02, T-03).
- **SC-02** — invalid or missing files must be rejected with a clear message (T-05, T-06).
- **SC-03 / SC-04** — empty or duplicate keywords must be rejected (T-08b, T-09b).
- **SC-05** — Process with no candidates or no keywords must show a message and not crash (T-12, T-12c).

So this technique is not a separate product feature; it is how the success criteria still hold for abnormal data.

![Invalid PDF rejected](criteria_d/screenshots/test_T05_invalid_pdf.png)

*Figure: Invalid data — uploading `resume.pdf` shows “only .txt files are allowed” (T-05) → protects SC-02.*

![Empty keyword rejected](criteria_d/screenshots/test_T08b_empty_keyword.png)

*Figure: Invalid data — empty keyword shows “Keyword cannot be empty” (T-08b) → protects SC-03.*

![Invalid login](criteria_d/screenshots/test_T02_invalid_login.png)

*Figure: Invalid data — wrong password shows “Invalid email or password” (T-02) → protects SC-01.*

---

## Teacher check: technique ↔ appendix ↔ success criteria

| # | Technique | Appendix A lines | Screenshot | Success criteria link |
|---|---|---|---|---|
| 1 | Password hashing and login | 39–40, 134–138 | `code_01_login_hash.png` | **SC-01** — email/password login |
| 2 | File reading and upload validation | 190–205 | `code_02_file_upload.png` | **SC-02**, **SC-08** — `.txt` upload and 10+ files |
| 3 | Linear search scoring | 90–97 | `code_03_linear_search.png` | **SC-05** — match score after Process |
| 4 | Bubble sort leaderboard | 99–108 | `code_04_bubble_sort.png` | **SC-06**, **SC-07** — sort + top-three highlight |
| 5 | SQLite parameterised queries | 309–314 | `code_05_sqlite.png` | **SC-05**, **SC-07** — persistent scores for leaderboard |
| 6 | Error handling for invalid data | 126–128, 303–306 | `code_06_error_handling.png` | **SC-01**, **SC-02**, **SC-03/04**, **SC-05** — criteria still hold on bad input |

Checked: every code screenshot matches Appendix A and contains pure code only (no comments).

---

## Test evidence (Observed Results)

Tests follow the Criterion C plan (Chrome; `hr@gmail.com` / `hr12345`; files in `sample_cvs/`).

| Test ID | SC | Description | Test Data | Observed Results |
|---|---|---|---|---|
| T-01 | SC-01 | Valid login | hr@gmail.com / hr12345 | Redirected to Dashboard. |
| T-02 | SC-01 | Invalid password | wrong123 | Error: “Invalid email or password.” Stayed on login. |
| T-03 | SC-01 | Empty login fields | empty | Error: “Please enter both email and password.” |
| T-04 | SC-02 | Valid .txt upload | 01_Karolina_Nowak.txt | File accepted; Karolina Nowak appears. |
| T-05 | SC-02 | Invalid file type | resume.pdf | Error: “only .txt files are allowed.” Not stored. |
| T-06 | SC-02 | No file selected | none | Error: “No file selected.” |
| T-07 | SC-08 | 10+ uploads | 12 .txt files | 12 candidates present after upload. |
| T-08 | SC-03 | Add keyword | Python | Keyword Python appears in the list. |
| T-08b | SC-03 | Empty keyword | empty string | Error: “Keyword cannot be empty.” |
| T-09b | SC-04 | Duplicate keyword | python (duplicate) | Error: keyword already in the list. |
| T-11 | SC-05 | Match scores | 12 candidates + 5 keywords | Name and score shown for each candidate. |
| T-12 | SC-05 | Process, no candidates | none | Error: “No candidates to process.” No crash. |
| T-12c | SC-05 | Process, no keywords | candidates only | Error: “No keywords to match.” |
| T-13 | SC-06 | Sorting | 12 scores | Descending order (17, 14, 12, 9, 8, …, 0). |
| T-14 | SC-07 | Leaderboard | full workflow | Numbered list of 12 candidates with scores. |
| T-15 | SC-07 | Top 3 highlight | ≥4 candidates | Ranks 1–3 highlighted in green. |

The strategy covers normal, abnormal and extreme data. One limitation is that bubble sort is checked through the final on-screen order, not a printout of every swap.

---

## AI (LLM) acknowledgment

An AI coding assistant (LLM) helped with Flask setup, debugging some upload/validation edge cases, and drafting notes for this Criterion D write-up. The main algorithm choices (linear search and bubble sort), the SQLite design, and the final wording were reviewed and decided by me. The same acknowledgment is in a short note at the top of the development file `app.py`. Appendix A itself is comment-free code only.

---

## Appendix reference

All excerpts refer to **Appendix A** (`APPENDIX_SOURCE_CODE.txt`). Screenshots used above are in `docs/criteria_d/screenshots/` and show the same comment-free lines.
