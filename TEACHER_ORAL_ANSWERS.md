# Short answers for the teacher interview

Use this sheet to practise out loud. Do **not** hand this file in as the appendix. The appendix is still `APPENDIX_SOURCE_CODE.txt`.

How to practise:

1. Open `APPENDIX_SOURCE_CODE.txt` next to this sheet.
2. Cover the answer. Ask yourself the question.
3. Say the answer in your own words. Then check.
4. Line numbers mean the clean code under `File: app.py` (or the HTML/CSS file named in that answer). Do not count the banner lines.

---

## 1. Where did you take the code from?

**Look at:** the top of `app.py` (imports), then `get_score` and `bubble_sort`.

**Say this:**
“The website structure follows the official Flask tutorial: one Python file, SQLite, session login, and HTML templates. Password hashing comes from Werkzeug. Database calls come from the Python sqlite3 documentation. File upload and flash messages follow Flask’s own examples. The linear search and the bubble sort are not from the web — they follow my Criterion C flowcharts.”

**Links if the teacher asks to open one:**
- Flask tutorial: https://flask.palletsprojects.com/en/stable/tutorial/
- Werkzeug passwords: https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security
- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- File upload: https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
- Flash messages: https://flask.palletsprojects.com/en/stable/patterns/flashing/

---

## 2. How does login work?

**Look at:** `app.py` lines 116–137 (`login`), and line 8 (`secret_key`).

**Say this:**
“The login page accepts email and password. If either box is empty, I show a message and stay on the page. Otherwise I look up the email in the User table and check the password against the stored hash. If it matches, I store the user id in the session and go to the dashboard. The secret key signs that session, so the browser cannot fake a login.”

---

## 3. Why is the password not stored as plain text?

**Look at:** `app.py` lines 35–36 and line 130.

**Say this:**
“When the database is created, `hr12345` is turned into a hash with `generate_password_hash` before it is saved. At login I use `check_password_hash` to test the typed password against that hash. Even if someone opens the database file, they do not see the real password. Those two functions come from Werkzeug.”

---

## 4. What happens when the user uploads files?

**Look at:** `app.py` lines 181–210 (`upload`), and lines 167–179 (`save_candidate`).

**Say this:**
“The form can send many `.txt` files at once. I reject a wrong file type and an empty file with a message, and I continue with the other files. The candidate’s name is the first line of the file, and the contact is the first word that contains `@`. If the same name already exists, I replace that candidate instead of creating a duplicate, and I delete the old score.”

---

## 5. How do the five keywords work?

**Look at:** `app.py` line 30 (Job table), lines 69–75 (`get_keyword_list`), and lines 224–244 (`add_keyword`).

**Say this:**
“There is one job per HR user, with five fixed columns: keyword1 to keyword5. Empty slots are empty strings. When the user adds a keyword, I refuse an empty word, a duplicate, or a sixth keyword. If it is allowed, I put it in the first empty slot. A helper builds a normal list of only the filled keywords for scoring.”

---

## 6. Where is the linear search, and how does the score work?

**Look at:** `app.py` lines 77–84 (`clean_words`) and lines 86–93 (`get_score`).

**Say this:**
“First I clean the resume into lowercase words and turn punctuation into spaces. Then `get_score` walks every word in the resume and compares it with every keyword. That nested loop is the linear search from my flowchart. Every match adds one point, so if Python appears four times, that is four points, not one.”

---

## 7. Where is the bubble sort, and why not use Python’s sort?

**Look at:** `app.py` lines 95–104 (`bubble_sort`) and line 164 in `dashboard`.

**Say this:**
“Each candidate is a small list: id, name, contact, score. Bubble sort compares neighbours and swaps them when the left score is smaller, so the highest score ends up first. I did not use Python’s built-in sort, because the algorithm has to be visible for the IA. Process only saves the scores. The dashboard sorts them when it draws the page.”

---

## 8. Why are the top three green?

**Look at:** `templates/dashboard.html` lines 82–87, and `static/style.css` lines 97–99.

**Say this:**
“After sorting, the template loops through the leaderboard. Jinja’s `loop.index` is the rank, starting at 1. Ranks 1, 2 and 3 get the class `top-three`. The stylesheet paints those cells light green and bold. The rank is not stored in the database — it is just the position after sorting.”

---

## 9. What happens if there are no candidates, or if Process is clicked with no keywords?

**Look at:** `app.py` lines 289–316 (`process`), especially lines 299–302.

**Say this:**
“Process first loads the candidates and the keyword list. If there are no candidates, I show a message and I do not score anything. If there are no keywords, I show another message. Only when both lists have something do I delete the old Match rows, score every resume, and save the new scores. The program does not crash.”

---

## 10. What is one limitation of your matching method?

**Look at:** `app.py` lines 86–93 (`get_score`).

**Say this:**
“Every occurrence of a keyword counts, so a candidate can raise the score by repeating the same word many times. That is fair to mention as a limitation. Also, keywords are compared as single words, so a phrase with a space will never match. A better next step would be to count each keyword at most once per resume.”

---

## Quick memory map

| Topic | Where in the clean appendix |
|-------|----------------------------|
| Sources / imports | `app.py` lines 1–4 |
| Open database | `app.py` lines 21–24 |
| Linear search | `app.py` lines 86–93 |
| Bubble sort | `app.py` lines 95–104 |
| Login | `app.py` lines 116–137 |
| Upload | `app.py` lines 181–210 |
| Add keyword | `app.py` lines 224–244 |
| Process | `app.py` lines 289–316 |
| Green top three | `dashboard.html` 82–87 + `style.css` 97–99 |

## One-minute opening (optional)

If the teacher asks you to introduce the program first:

“This is a small website for one HR user. They log in, upload candidate text files, enter up to five job keywords, and click Process. The program scores each resume with a linear search, sorts the candidates with bubble sort, and highlights the top three in green.”
