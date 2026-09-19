# Candidate Matcher — line-by-line explanation

This file is for you, not for the appendix. The file you give the teacher is `APPENDIX_SOURCE_CODE.txt`. That file has the same code and no comments.

How to use this during the interview:

1. Open `APPENDIX_SOURCE_CODE.txt`.
2. Each file inside it is numbered here starting at **1**. Do not count the banner lines (`File: app.py`). Count only the code under that banner.
3. If the teacher points at a line, find that line number in the matching section below and read the “Say this” sentence in your own words.

The program is a small website. One HR person logs in, uploads candidate text files, keeps up to five job keywords, clicks Process, and sees the candidates sorted from the highest match score to the lowest. The top three rows are green.

Two algorithms are written by hand:

- **Linear search** counts how many times the keywords appear in a resume (`get_score`).
- **Bubble sort** orders the candidates (`bubble_sort`).

There is no JavaScript. Every button sends a form, Python does the work, and the page is drawn again from the database.

---

# File: app.py

## Lines 1–4 — imports

**Line 1** `import os`

This loads Python’s operating-system tools. Later the program uses them to find its own folder and to read the sample resume files. It is not used for the database.

**Say this:** “`os` is for folders and files on the computer. I use it to locate the sample CVs.”

**Line 2** `import sqlite3`

This loads Python’s built-in SQLite library. SQLite is a database stored in one file (`matcher.db`). The program uses `sqlite3` to create tables, insert rows, and read them back.

**Say this:** “I do not install a separate database server. `sqlite3` comes with Python and stores everything in one file.”

**Line 3** `from flask import Flask, render_template, request, redirect, url_for, session, flash`

This loads only the Flask tools this program needs:

- `Flask` — the website itself.
- `render_template` — fills an HTML page with data and sends it to the browser.
- `request` — reads what the browser sent (the form, the password, the uploaded files).
- `redirect` — sends the browser to a different page.
- `url_for` — builds a web address from a function name, so if a route changes, the links still work.
- `session` — remembers who is logged in between clicks.
- `flash` — stores a short message to show on the next page (“3 file(s) uploaded.”).

**Say this:** “Flask is the library that turns this Python file into a website. I only import the pieces I actually use.”

**Line 4** `from werkzeug.security import generate_password_hash, check_password_hash`

Werkzeug is the library Flask is built on. These two functions handle passwords. `generate_password_hash` turns `hr12345` into a long scrambled string. `check_password_hash` checks a typed password against that string. The real password is never stored.

**Say this:** “The password is stored as a hash, not as plain text. Even if someone opens the database, they do not see `hr12345`.”

**Line 5** *(blank)*

A blank line does not run. It only separates the imports from the setup below.

## Lines 6–19 — settings

**Line 6** `app = Flask(__name__)`

This creates the website object and stores it in `app`. Every page is attached to this object later with `@app.route`. `__name__` is the name of this file. Flask uses it to find the `templates` folder and the `static` folder sitting next to `app.py`.

**Say this:** “This one line creates the web application. Flask then knows where my HTML and CSS files are.”

**Line 7** *(blank)*

Separates the app object from its secret key.

**Line 8** `app.secret_key = "ib-computer-science-ia-secret"`

The secret key signs the login cookie. Flask stores `user_id` in that cookie. Because it is signed with this key, the user cannot edit the cookie and pretend to be someone else. If this string changed, everyone would be logged out.

**Say this:** “The secret key protects the login memory. It is not the HR password. The HR password is `hr12345`, stored as a hash in the database.”

**Line 9** *(blank)*

Separates the secret key from the constants.

**Line 10** `MAX_KEYWORDS = 5`

A constant: the job can have at most five keywords. The name is in capitals so it is easy to see that this number should not change while the program runs. The Job table has columns `keyword1` to `keyword5` for the same reason. Using one name means the limit is not typed as a raw `5` in every loop.

**Say this:** “Five is a design choice from my success criteria. I put it in one place so every check uses the same limit.”

**Line 11** *(blank)*

Separates constants.

**Line 12** `PROGRAM_FOLDER = os.path.dirname(os.path.abspath(__file__))`

`__file__` is the path of `app.py`. `os.path.abspath` makes it a full path. `os.path.dirname` drops the file name and keeps the folder. That folder is where `sample_cvs` lives. This still works if the program is started from a different folder.

**Say this:** “This finds the folder the program is in, so I can open the sample resumes no matter where I click Run.”

**Line 13** *(blank)*

Separates the folder path from the online-demo check.

**Line 14** `ONLINE_DEMO = os.environ.get("VERCEL") is not None`

`os.environ` is the list of environment variables, which are settings the computer gives the program when it starts. The free hosting service used for the phone demo is called Vercel, and it sets a variable named `VERCEL`. `.get("VERCEL")` returns that value, or `None` if it is missing. `is not None` is `True` only on that server, and `False` on a normal computer.

**Say this:** “This is only for the online demo. On my computer this is False, so the next lines use a normal database file. You can ignore this if we are looking at the local program.”

**Line 15** *(blank)*

Separates the test from the two possible database paths.

**Line 16** `if ONLINE_DEMO:`

Starts the branch. The indented line under it runs only when the program is on the hosting server.

**Line 17** `DATABASE_FILE = "/tmp/matcher.db"`

On that server the project folder cannot be written to, and it can be wiped. `/tmp` is a temporary folder that can be written. The database is created there. That is why the online demo can reset.

**Say this:** “The online copy cannot save into the project folder, so the database goes in a temporary folder. That is why demo data can disappear. My own computer does not do this.”

**Line 18** `else:`

The other branch: a normal computer.

**Line 19** `DATABASE_FILE = "matcher.db"`

On your computer the database file is named `matcher.db` and is created in the folder where you start the program. Deleting that file resets candidates, keywords, and scores. The tables are created again the next time the program starts.

**Say this:** “Locally, all data is in `matcher.db`. Delete that file and the program starts fresh.”

**Line 20** *(blank)*

Separates setup from the first function.

## Lines 21–24 — open the database

**Line 21** `def get_db():`

Defines a function named `get_db`. It takes no inputs. Every function that needs the database calls this instead of repeating the open steps. The pattern is: open, do the work, close.

**Say this:** “I made one function that opens the database so I do not copy those three lines everywhere.”

**Line 22** `connection = sqlite3.connect(DATABASE_FILE)`

Opens `matcher.db`, or creates it if it does not exist yet. `connection` is the open link. Nothing is saved permanently until `commit` is called.

**Say this:** “`connect` opens the file. If the file is missing, SQLite creates an empty one.”

**Line 23** `connection.row_factory = sqlite3.Row`

By default a row comes back as a tuple, so you must remember that column 0 is the id and column 1 is the email. `sqlite3.Row` lets the program use names: `user["email"]`, `candidate["name"]`. That matches the columns in the ERD.

**Say this:** “This line is why I can write `row["name"]` instead of `row[1]`. It makes the code match the table columns.”

**Line 24** `return connection`

Sends the open connection back to whoever called `get_db`. The caller must close it later.

**Say this:** “The function gives the connection back. The caller closes it when it is finished.”

**Line 25** *(blank)*

Separates functions.

## Lines 26–42 — create tables and the HR account

**Line 26** `def init_db():`

Defines the function that prepares the database. It is called once at the bottom of the file, when the program starts. It is safe to run again because of `IF NOT EXISTS`.

**Say this:** “`init_db` runs at startup. It creates the tables only if they are not already there, so restarting does not wipe data.”

**Line 27** `db = get_db()`

Opens the database and stores the connection in `db`.

**Line 28** `db.execute("CREATE TABLE IF NOT EXISTS User (user_id INTEGER PRIMARY KEY, email TEXT, password_hash TEXT)")`

`execute` runs one SQL statement.

- `CREATE TABLE IF NOT EXISTS` creates the table only when it is missing.
- `User` is the table from the ERD.
- `user_id INTEGER PRIMARY KEY` is the unique id. SQLite fills it in automatically, starting at 1.
- `email TEXT` stores the login email.
- `password_hash TEXT` stores the scrambled password, not the real one.

**Say this:** “This is the User table from my ERD: id, email, and the hashed password.”

**Line 29** `db.execute("CREATE TABLE IF NOT EXISTS Candidate (cand_id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, contact TEXT, resume_text TEXT)")`

Creates the Candidate table:

- `cand_id` — unique id of the candidate.
- `user_id` — which HR user owns this candidate. In this program that is always the one HR account.
- `name` — first line of the uploaded file.
- `contact` — the first word that contains `@`, or `"not found"`.
- `resume_text` — the whole file, because scoring reads the full text later.

**Say this:** “The candidate row keeps the name, the contact, and the full resume, because the score is calculated from the full text.”

**Line 30** `db.execute("CREATE TABLE IF NOT EXISTS Job (job_id INTEGER PRIMARY KEY, user_id INTEGER, keyword1 TEXT, keyword2 TEXT, keyword3 TEXT, keyword4 TEXT, keyword5 TEXT)")`

Creates the Job table. There is one job per HR user. The five keywords are five columns, not a separate table. An empty slot is stored as an empty string `""`, not as a missing row.

**Say this:** “I did not make a fifth table for keywords. The ERD has five columns on Job, so the code has `keyword1` to `keyword5`.”

**Line 31** `db.execute("CREATE TABLE IF NOT EXISTS Match (match_id INTEGER PRIMARY KEY, cand_id INTEGER, job_id INTEGER, match_score INTEGER)")`

Creates the Match table. One row means “this candidate, for this job, scored this many points.” The score is stored here, not on the Candidate row, because that is what the ERD says. A candidate with no Match row has not been processed yet.

**Say this:** “Match is the link between a candidate and the job. The score lives here.”

**Line 32** *(blank)*

Separates “create tables” from “add the first user”.

**Line 33** `user = db.execute("SELECT * FROM User WHERE email = ?", ("hr@gmail.com",)).fetchone()`

Looks for the HR account.

- `SELECT *` means all columns.
- `WHERE email = ?` filters to one email. The `?` is a placeholder.
- `("hr@gmail.com",)` is the value that replaces `?`. The comma makes it a one-item tuple, which `execute` requires.
- The email is not pasted into the SQL text. That is the safe way to pass values.
- `fetchone()` returns the first matching row, or `None` if nobody has that email.

**Say this:** “I search for `hr@gmail.com`. The question mark is a placeholder, so the email is data, not part of the SQL command.”

**Line 34** `if user is None:`

`None` means the account does not exist yet. The lines under this run only the first time, or after `matcher.db` is deleted.

**Line 35** `password_hash = generate_password_hash("hr12345")`

Turns the password `hr12345` into a hash. A hash cannot be reversed back into the password. The same password hashed twice will not look identical, because a random salt is mixed in, but `check_password_hash` can still test it.

**Say this:** “Here I hash `hr12345` before it ever touches the database.”

**Line 36** `db.execute("INSERT INTO User (email, password_hash) VALUES (?, ?)", ("hr@gmail.com", password_hash))`

Inserts one User row. The two `?` marks are filled by the tuple: email, then hash. SQLite assigns `user_id` 1 to this first row.

**Say this:** “This writes the HR account. The id becomes 1 because it is the first row.”

**Line 37** `db.execute("INSERT INTO Job (user_id, keyword1, keyword2, keyword3, keyword4, keyword5) VALUES (1, '', '', '', '', '')")`

Creates the one job for that user. `user_id` is written as `1` because the user just inserted is the first user. All five keyword slots start empty. Empty is `''`, two quotes with nothing between them.

**Say this:** “Every HR user has exactly one job. At the start all five keyword slots are empty strings.”

**Line 38** `if ONLINE_DEMO:`

Only the hosted demo loads sample data automatically. On your computer this is skipped, so you start with an empty candidate list, which matches the tests where you upload files yourself.

**Line 39** `load_demo_data(db)`

Calls the function defined just below. In Python that is allowed, because this line does not run while the file is being read. It runs later, when `init_db()` is called, and by then `load_demo_data` already exists.

**Say this:** “This call looks like it uses a function that is written lower down. That is fine, because Python reads the whole file before `init_db` actually runs.”

**Line 40** *(blank)*

Closes the visual block of the `if user is None` section.

**Line 41** `db.commit()`

Writes the pending changes to the file. Until `commit`, inserts can still be lost. Create-table and insert both wait for this.

**Say this:** “`commit` is the save button for the database.”

**Line 42** `db.close()`

Closes the connection and releases the file. Every open should have a close.

**Line 43** *(blank)*

Separates functions.

## Lines 44–56 — sample data for the online demo only

**Line 44** `def load_demo_data(db):`

Defines a function that receives the already-open connection `db`. It does not open its own connection, and it does not commit. The caller (`init_db`) commits afterwards. This function is not used in the local IA tests.

**Say this:** “This whole function is only for the online demo. The scoring algorithm does not depend on it.”

**Line 45** `db.execute("UPDATE Job SET keyword1 = 'Python', keyword2 = 'Flask', keyword3 = 'SQL', "`

Updates the job that belongs to user 1. The statement is split across two lines because it is long. Python joins adjacent strings inside the parentheses. The five demo keywords are Python, Flask, SQL, Communication, and Teamwork.

**Line 46** `"keyword4 = 'Communication', keyword5 = 'Teamwork' WHERE user_id = 1")`

The rest of that SQL. `WHERE user_id = 1` makes sure only that job is changed. These values are fixed demo words, not typed by a stranger, so they are written directly in the SQL text.

**Say this:** “On the demo, the five example keywords are filled in so a visitor can press Process immediately.”

**Line 47** `folder = os.path.join(PROGRAM_FOLDER, "sample_cvs")`

Builds the path to the `sample_cvs` folder. `os.path.join` inserts the correct slash for the operating system.

**Line 48** `for file_name in sorted(os.listdir(folder)):`

`os.listdir` returns every name in that folder. `sorted` puts them in alphabetical order, so `01_Karolina_Nowak.txt` comes before `02_...`. The loop runs once per name.

**Say this:** “I read the sample folder in sorted order so the demo candidates are inserted in a stable order.”

**Line 49** `if file_name.endswith(".txt"):`

Skips anything that is not a text file, such as the `bad_files` folder entry. Only `.txt` resumes are loaded.

**Line 50** `sample_file = open(os.path.join(folder, file_name), encoding="utf-8")`

Opens one resume. `encoding="utf-8"` means letters like `ł` or accented characters are read correctly. This is a sample file on disk, not an upload from the browser.

**Line 51** `resume_text = sample_file.read()`

Reads the entire file into one string.

**Line 52** `sample_file.close()`

Closes the file. The resume text is already in memory.

**Line 53** `name = resume_text.strip().split("\n")[0].strip()`

This is the name rule, used again on upload:

- `strip()` removes spaces and blank lines at the ends.
- `split("\n")` cuts the text into lines.
- `[0]` takes the first line.
- `strip()` again removes spaces around that line.

For the sample file, the first line is `Karolina Nowak`, so that becomes the name.

**Say this:** “The candidate’s name is always the first line of the file. I do not ask the user to type the name separately.”

**Line 54** `contact = find_contact(resume_text)`

Calls the function on line 106. It returns the first word containing `@`, for example `karolina.nowak@gmail.com`.

**Line 55** `db.execute("INSERT INTO Candidate (user_id, name, contact, resume_text) VALUES (1, ?, ?, ?)",`

Inserts one candidate owned by user 1. The three `?` marks are filled on the next line. `cand_id` is left out so SQLite generates it.

**Line 56** `(name, contact, resume_text))`

The three values for those placeholders, in the same order as the `?` marks.

**Line 57** *(blank)*

Separates functions.

## Lines 58–67 — login check and the current job

**Line 58** `def is_logged_in():`

Defines a yes/no function. Every dashboard action starts by calling it.

**Line 59** `if "user_id" in session:`

`session` is Flask’s memory of this browser. After a successful login, `user_id` is stored there. `in` checks whether that key exists.

**Line 60** `return True`

If the key exists, the person is logged in. `return` stops the function immediately.

**Line 61** `return False`

If the key is missing, the person is not logged in. This line runs only when the `if` was false.

**Say this:** “Logged in means the session contains `user_id`. Nothing else is checked here. The password was already checked on the login page.”

**Line 62** *(blank)*

Separates functions.

**Line 63** `def get_job():`

Defines a function that loads the one job of the logged-in user. No argument is needed because the user id is in the session.

**Line 64** `db = get_db()`

Opens the database.

**Line 65** `job = db.execute("SELECT * FROM Job WHERE user_id = ?", (session["user_id"],)).fetchone()`

Reads the job row whose `user_id` matches the logged-in person. `fetchone()` is correct because each user has exactly one job. The result includes `job_id` and all five keyword columns.

**Line 66** `db.close()`

Closes the database before returning. The row data is already in `job`, so closing does not erase it.

**Line 67** `return job`

Gives that row back. Callers then read `job["keyword1"]`, `job["job_id"]`, and so on.

**Line 68** *(blank)*

Separates functions.

## Lines 69–75 — turn the five slots into a list

**Line 69** `def get_keyword_list(job):`

Takes a job row and returns a normal Python list of the keywords that are actually filled in. Empty slots are left out. Scoring uses this list.

**Line 70** `keyword_list = []`

Starts with an empty list. `[]` means a list with no items.

**Line 71** `for slot in range(1, MAX_KEYWORDS + 1):`

`range(1, 6)` produces 1, 2, 3, 4, 5. The stop value is not included, so `MAX_KEYWORDS + 1` is required. `slot` is the column number.

**Say this:** “`range` stops before the second number, so I add 1 to get slots 1 through 5.”

**Line 72** `keyword = job["keyword" + str(slot)]`

Builds the column name. When `slot` is 1, `"keyword" + "1"` is `"keyword1"`. `str(slot)` is needed because a number cannot be added to a string with `+`. Then the row is read by that column name.

**Line 73** `if keyword != "":`

Keeps only real keywords. An empty string is an unused slot.

**Line 74** `keyword_list.append(keyword)`

Adds that keyword to the end of the list.

**Line 75** `return keyword_list`

Returns something like `["Python", "Flask", "SQL"]`. If every slot is empty, the list is empty, and Process will refuse to run.

**Line 76** *(blank)*

Separates the helper from the algorithms.

## Lines 77–84 — clean the resume into words

**Line 77** `def clean_words(text):`

Prepares a resume for comparison. The input is the full resume string. The output is a list of lowercase words with punctuation removed.

**Line 78** `cleaned = ""`

Starts an empty string. The loop will build a new string one character at a time. The original text is not changed.

**Line 79** `for character in text.lower():`

`text.lower()` returns a new string where `P` becomes `p`. The loop visits every character of that lowercase copy, including spaces and commas.

**Say this:** “I lowercase first so `Python` and `python` count as the same word.”

**Line 80** `if character.isalnum():`

`isalnum()` is true when the character is a letter or a digit. It is false for spaces, commas, periods, and `@`.

**Line 81** `cleaned = cleaned + character`

If it is a letter or digit, it is glued onto the result. So the letters of `Python` stay together.

**Line 82** `else:`

Every other character takes this branch.

**Line 83** `cleaned = cleaned + " "`

A comma, period, or other symbol becomes a space. That is why `Python,` becomes the word `python` instead of `python,`. The `@` in an email is also replaced, but contact extraction happens earlier, on the original text, so the email is already saved.

**Say this:** “Punctuation becomes a space. That is why a comma after a skill does not stop the match.”

**Line 84** `return cleaned.split()`

`split()` with no argument cuts on any whitespace and throws away the extra spaces. `"python  flask"` becomes `["python", "flask"]`.

**Example you can say:** “The text `Python, Flask.` becomes the list `python`, `flask`.”

**Line 85** *(blank)*

Separates the two scoring functions.

## Lines 86–93 — linear search score

**Line 86** `def get_score(resume_text, keyword_list):`

The linear search. Inputs are the full resume and the list of keywords. Output is one integer, the match score.

**Line 87** `words = clean_words(resume_text)`

Turns the resume into the clean word list from the previous function.

**Line 88** `score = 0`

Starts at zero. Every hit will add 1.

**Line 89** `for word in words:`

Outer loop: walk through the resume from the first word to the last. This is the “linear” part: each word is visited once, in order, with no skipping and no index jump.

**Line 90** `for keyword in keyword_list:`

Inner loop: for that one resume word, compare it with every keyword. With 5 keywords, each resume word is compared up to 5 times.

**Say this:** “This is a nested loop. For every word in the CV I check every keyword. That is the linear search on my flowchart.”

**Line 91** `if word == keyword.lower().strip():`

Equal means the same text.

- `keyword.lower()` ignores capitals, so the resume word `python` matches the keyword `Python`.
- `.strip()` removes spaces the user may have typed around the keyword.
- `==` is exact. `python` does not match `py`, and it does not match `python3` unless that exact token is the keyword.
- A keyword with a space, such as `web developer`, will never equal a single resume word, so it scores 0. Keywords are meant to be single words.

**Line 92** `score = score + 1`

One hit, one point. If `Python` appears four times, that is 4 points, not 1. Repeating a word increases the score. That matches the criterion, and it is also a limitation: a candidate could stuff a keyword to rank higher.

**Say this:** “I count every occurrence, not just yes or no. Four mentions of Python are four points. I would mention that as a limitation in the evaluation.”

**Line 93** `return score`

After both loops finish, the total is returned. A resume with no hits returns 0, and 0 is still a valid score that gets stored.

**Line 94** *(blank)*

Separates scoring from sorting.

## Lines 95–104 — bubble sort

**Line 95** `def bubble_sort(candidate_list):`

Sorts the list in place, highest score first. Python’s built-in `sort` is not used, so the algorithm is visible. Each item looks like `[cand_id, name, contact, score]`.

**Line 96** `n = len(candidate_list)`

`len` is the number of candidates. If there are 12, `n` is 12.

**Line 97** `for i in range(n - 1):`

Outer pass. With 12 candidates this is `range(11)`, so `i` goes from 0 to 10. After each pass, one more score is in its final place at the end, so the next pass can be shorter. `n - 1` passes are enough to sort `n` items.

**Line 98** `for j in range(n - 1 - i):`

Inner pass. `j` is the left index of a pair. The first pass compares indexes 0-1, 1-2, 2-3, and so on, up to the end. The next pass stops one earlier because the last item is already the smallest remaining score.

**Say this:** “The inner loop compares neighbours. Subtracting `i` makes each pass shorter, because the end of the list is already sorted.”

**Line 99** `left = candidate_list[j]`

The candidate at position `j`. This is a whole small list, not just the score.

**Line 100** `right = candidate_list[j + 1]`

The next candidate, the right neighbour.

**Line 101** `if left[3] < right[3]:`

Index 3 is the score, because the item was built as `[cand_id, name, contact, score]`. The test is “is the left score smaller than the right score?”. If yes, they are in the wrong order for a highest-first list, so they must be swapped. If the scores are equal, the test is false, so they stay in their current order. That keeps the earlier upload first when scores tie.

**Say this:** “Index 3 is the score. I swap only when the left score is smaller, so the bigger score moves left. Equal scores are not swapped.”

**Line 102** `candidate_list[j] = right`

The swap, first half. Position `j` now holds what used to be on the right. The old left value is still in the variable `left`, so it is not lost.

**Line 103** `candidate_list[j + 1] = left`

The swap, second half. Position `j + 1` receives the old left candidate. The two neighbours have exchanged places.

**Line 104** `return candidate_list`

Returns the same list, now ordered. Returning it makes the call `leaderboard = bubble_sort(scored_list)` easy to read. The original list object was also changed inside the function.

**Worked example you can say:** “Suppose scores 2, 5, 2. First pair 2 and 5: 2 is smaller, so they swap to 5, 2, 2. Next pair 2 and 2: equal, no swap. The highest score is now first.”

**Line 105** *(blank)*

Separates functions.

## Lines 106–110 — find the email

**Line 106** `def find_contact(text):`

Searches the original resume text, before punctuation is stripped, for a contact.

**Line 107** `for word in text.split():`

`split()` cuts the original text on spaces. The loop looks at each word.

**Line 108** `if "@" in word:`

The first word that contains the @ sign is treated as the email. In the sample file that word is `karolina.nowak@gmail.com`. Words like `Email:` do not contain `@`, so they are skipped.

**Line 109** `return word`

Returns that word immediately. Later words are not checked. If a resume had two emails, only the first would be kept.

**Line 110** `return "not found"`

If the loop ends with no `@`, there is no email. The function returns the text `not found` so the table still has something to show. This is not an error and it does not stop the upload.

**Say this:** “Contact means the first word with an @ sign. If there is none, I store the words not found. I do not try to read the phone number.”

**Line 111** *(blank)*

Separates helpers from pages.

## Lines 112–114 — the start address

**Line 112** `@app.route("/")`

A decorator. It connects the function below to the address `/`, which is the site root, for example `http://localhost:5000/`. When the browser asks for that address, Flask calls `index`.

**Say this:** “The `@` line is not a normal call. It registers the next function as the page for that address.”

**Line 113** `def index():`

The function for the root address. It does not draw a page of its own.

**Line 114** `return redirect(url_for("login"))`

`url_for("login")` builds the address of the `login` function, which is `/login`. `redirect` tells the browser to go there. So opening the site always lands on the login page.

**Line 115** *(blank)*

Separates routes.

## Lines 116–137 — login

**Line 116** `@app.route("/login", methods=["GET", "POST"])`

Registers `/login`. `methods` lists the allowed request types. GET means “show the page”. POST means “the form was submitted”. Both are needed: first the empty form, then the email and password.

**Line 117** `def login():`

The login function. Flask calls it for both GET and POST. The code inside decides which one happened.

**Line 118** `if request.method == "POST":`

True only when the user pressed Login. If they only opened the page, this is false and the function jumps to line 137.

**Line 119** `email = request.form["email"].strip()`

`request.form` is the submitted form. `"email"` matches `name="email"` on the HTML input. `.strip()` removes spaces the user typed by accident, so `" hr@gmail.com "` still matches.

**Line 120** `password = request.form["password"]`

Reads the password. It is not stripped, because a space could be part of a password. It is not printed and it is not stored.

**Line 121** *(blank)*

Separates reading the form from checking it.

**Line 122** `if email == "" or password == "":`

True if either box was left empty. `or` means one empty box is enough. This is test T-03.

**Line 123** `flash("Please enter both email and password.")`

Stores that sentence for the next page. The HTML page prints flashed messages at the top.

**Line 124** `return render_template("login.html")`

Draws the login page again and stops. The password is not checked, because there is nothing useful to check. `return` is important: without it, the function would continue and show “Invalid email or password” as well.

**Say this:** “Empty fields get their own message, and I return immediately so I do not also say the password is wrong.”

**Line 125** *(blank)*

Separates the empty check from the database lookup.

**Line 126** `db = get_db()`

Opens the database to look up the user.

**Line 127** `user = db.execute("SELECT * FROM User WHERE email = ?", (email,)).fetchone()`

Searches the User table for the typed email. `fetchone()` is `None` if that email is not in the table.

**Line 128** `db.close()`

Closes the database before testing the password. The user row is already loaded.

**Line 129** *(blank)*

Separates the lookup from the decision.

**Line 130** `if user is None or not check_password_hash(user["password_hash"], password):`

Two failure cases, joined by `or`:

- `user is None` — no such email.
- `not check_password_hash(...)` — the email exists, but the password does not match the stored hash.

`check_password_hash` takes the stored hash first, then the typed password. `not` flips a failed check into True, so the error branch runs. A wrong password such as `wrong123` hits this line. The message is the same for a bad email and a bad password, so the program does not reveal which one was wrong.

**Say this:** “I use one message for both failures. I do not tell the person whether the email exists.”

**Line 131** `flash("Invalid email or password.")`

Stores the error message.

**Line 132** `return render_template("login.html")`

Shows the login page again. The session is not set, so the person is still logged out.

**Line 133** *(blank)*

Separates failure from success.

**Line 134** `session["user_id"] = user["user_id"]`

Success. The user’s id is stored in the session cookie. Later pages read `session["user_id"]` to know who is logged in. The password is not stored in the session.

**Line 135** `return redirect(url_for("dashboard"))`

Sends the browser to the dashboard. A redirect is used instead of drawing the dashboard here, so the address bar shows `/dashboard` and a refresh does not resubmit the password.

**Say this:** “After a correct login I save only the user id, then I redirect. The password is not kept in the session.”

**Line 136** *(blank)*

Separates the POST block from the GET line. The blank line is inside the function, before the final return.

**Line 137** `return render_template("login.html")`

This line runs when the method was not POST, meaning a normal visit. It shows the empty login form. No database check happens.

**Line 138** *(blank)*

Separates routes.

## Lines 139–142 — logout

**Line 139** `@app.route("/logout")`

Registers the address `/logout`. The method list is omitted, so only GET is allowed. The logout link on the page is a normal link, which is a GET.

**Line 140** `def logout():`

The logout function.

**Line 141** `session.clear()`

Deletes everything in the session, including `user_id`. The browser is no longer logged in. This does not delete candidates or scores from the database.

**Line 142** `return redirect(url_for("login"))`

Sends the browser back to the login page.

**Say this:** “Logout only forgets the session. The database is unchanged, so when I log in again the scores are still there. That is test T-16.”

**Line 143** *(blank)*

Separates routes.

## Lines 144–165 — dashboard

**Line 144** `@app.route("/dashboard")`

Registers `/dashboard`. GET only. The page is drawn from the database every time it is opened.

**Line 145** `def dashboard():`

The main page function.

**Line 146** `if not is_logged_in():`

`not` flips the boolean. If nobody is logged in, the body runs. This blocks someone who types `/dashboard` into the address bar without logging in.

**Line 147** `return redirect(url_for("login"))`

Sends them to login and stops. The rest of the function does not run.

**Line 148** *(blank)*

Separates the guard from the data loading.

**Line 149** `job = get_job()`

Loads the keyword row for this user. The page needs it to show the five slots, and the score lookup needs `job_id`.

**Line 150** `db = get_db()`

Opens the database for the candidate and match queries.

**Line 151** `candidates = db.execute("SELECT * FROM Candidate WHERE user_id = ? ORDER BY cand_id", (session["user_id"],)).fetchall()`

Reads every candidate that belongs to this HR user.

- `WHERE user_id = ?` means one user cannot see another user’s candidates. There is only one user in this product, but the column is still used.
- `ORDER BY cand_id` is upload order, oldest id first.
- `fetchall()` returns every row, as a list. `fetchone()` would have returned only the first.

**Line 152** *(blank)*

Separates the query from the two result lists.

**Line 153** `scored_list = []`

Candidates who already have a Match row will go here, then be bubble-sorted.

**Line 154** `unscored_list = []`

Candidates uploaded after the last Process have no Match row. They go here and are shown under “Not scored yet”. They are not mixed into the leaderboard with a fake zero, because a real score of 0 is different from “not processed”.

**Say this:** “I keep two lists. A score of zero is a real result. No row in Match means not scored yet.”

**Line 155** `for candidate in candidates:`

One pass over every candidate of this user.

**Line 156** `match = db.execute("SELECT match_score FROM Match WHERE cand_id = ? AND job_id = ?",`

Looks up this candidate’s score for this job. Only the score column is needed. The statement continues on the next line. `AND` means both conditions must be true: the right candidate and the right job.

**Line 157** `(candidate["cand_id"], job["job_id"])).fetchone()`

The two values for the two `?` marks. `fetchone()` is the row, or `None` if Process has not scored this candidate.

**Line 158** `if match is None:`

No score stored.

**Line 159** `unscored_list.append([candidate["cand_id"], candidate["name"], candidate["contact"], 0])`

Adds a four-item list: id, name, contact, and a placeholder 0. The page does not print that 0 for this list; it prints the words “not scored yet”. The 0 keeps the shape the same as the scored items. The id is kept so the Remove button knows which row to delete.

**Line 160** `else:`

There is a Match row.

**Line 161** `scored_list.append([candidate["cand_id"], candidate["name"], candidate["contact"], match["match_score"]])`

Same four-item shape, but item 3 is the real score from the database. Bubble sort reads that index.

**Line 162** `db.close()`

All queries are done, so the database is closed before sorting. Sorting does not need the database; it works on the Python lists.

**Line 163** *(blank)*

Separates loading from sorting and drawing.

**Line 164** `leaderboard = bubble_sort(scored_list)`

Sorts the scored candidates, highest score first. The unscored list is not sorted, because those people have no score yet.

**Line 165** `return render_template("dashboard.html", job=job, leaderboard=leaderboard, unscored_list=unscored_list)`

Fills `templates/dashboard.html` and sends it to the browser. The names `job`, `leaderboard`, and `unscored_list` become variables inside that HTML file. This is how Python data reaches the page.

**Say this:** “The dashboard function does not contain HTML. It prepares the data and hands it to the template.”

**Line 166** *(blank)*

Separates the page from the actions.

## Lines 167–179 — save one candidate

**Line 167** `def save_candidate(name, contact, resume_text):`

Saves one resume. It is a normal function, not a page. `upload` calls it after the file has been checked.

**Line 168** `db = get_db()`

Opens the database.

**Line 169** `existing = db.execute("SELECT cand_id FROM Candidate WHERE user_id = ? AND name = ?",`

Looks for a candidate with the same name for this same HR user. Only the id is needed.

**Line 170** `(session["user_id"], name)).fetchone()`

The two placeholder values. `fetchone()` is `None` if this name is new.

**Line 171** `if existing is None:`

New candidate. Insert a row.

**Line 172** `db.execute("INSERT INTO Candidate (user_id, name, contact, resume_text) VALUES (?, ?, ?, ?)",`

Insert with four placeholders: owner, name, contact, full text.

**Line 173** `(session["user_id"], name, contact, resume_text))`

The four values, in that order.

**Line 174** `else:`

The name already exists. Do not insert a second copy.

**Line 175** `db.execute("UPDATE Candidate SET contact = ?, resume_text = ? WHERE cand_id = ?",`

Changes the old row instead. The name stays the same. Contact and resume text are replaced.

**Line 176** `(contact, resume_text, existing["cand_id"]))`

The new contact, the new text, and the id of the row being updated.

**Line 177** `db.execute("DELETE FROM Match WHERE cand_id = ?", (existing["cand_id"],))`

Deletes the old score. The resume changed, so the old score would be a lie until Process is clicked again. The candidate then shows under “Not scored yet”.

**Say this:** “If I upload the same name twice, I replace the old resume and I delete the old score. I do not create a duplicate.”

**Line 178** `db.commit()`

Saves the insert or the update, and the score deletion if there was one.

**Line 179** `db.close()`

Closes the connection.

**Line 180** *(blank)*

Separates the helper from the upload page.

## Lines 181–210 — upload

**Line 181** `@app.route("/upload", methods=["POST"])`

Registers `/upload`. POST only. There is no page to GET; the form lives on the dashboard and submits here.

**Line 182** `def upload():`

Handles the Upload button.

**Line 183** `if not is_logged_in():`

Same guard as the dashboard. A logged-out person cannot post a file to this address.

**Line 184** `return redirect(url_for("login"))`

Sends them to login.

**Line 185** *(blank)*

Separates the guard from the file handling.

**Line 186** `files = request.files.getlist("files")`

`request.files` holds uploads. `"files"` matches `name="files"` on the file input. `getlist` is used because the input has `multiple`, so there can be many files. The result is a list.

**Line 187** `if len(files) == 0 or files[0].filename == "":`

Two ways the user pressed Upload without choosing a file. Sometimes the list is empty. Sometimes it contains one empty upload whose filename is `""`. Either one is “nothing selected”. This is test T-06.

**Line 188** `flash("No file selected.")`

Stores the message.

**Line 189** `return redirect(url_for("dashboard"))`

Goes back to the dashboard, where the message is shown. `return` stops the function so it does not try to read a missing file.

**Line 190** *(blank)*

Separates the empty check from the loop.

**Line 191** `saved_count = 0`

Counts how many files were actually stored. Rejected files do not increase it.

**Line 192** `for file in files:`

One iteration per selected file. A bad file does not stop the others.

**Line 193** `if not file.filename.lower().endswith(".txt"):`

`.lower()` makes `RESUME.TXT` still count as txt. `endswith(".txt")` checks the extension. `not` means “reject anything else”, including `resume.pdf`. The browser hint `accept=".txt"` can be bypassed, so the real check is here. This is test T-05.

**Line 194** `flash("File " + file.filename + " was rejected: only .txt files are allowed.")`

Builds the message by joining strings with `+`. The file name is included so the user knows which file failed when several were selected.

**Line 195** `continue`

Skips the rest of this loop iteration and moves to the next file. It is not `return`, because other files should still be processed.

**Say this:** “`continue` means skip this file only. One PDF does not cancel the text files selected with it.”

**Line 196** `try:`

Starts a protected block. Reading a file can fail. The matching `except` is on line 205. This is the file-upload try/except from Criterion B.

**Line 197** `resume_text = file.read().decode("utf-8", "ignore")`

`file.read()` returns bytes. `.decode("utf-8", "ignore")` turns bytes into text. `"ignore"` drops characters that are not valid UTF-8 instead of crashing.

**Line 198** `if resume_text.strip() == "":`

`strip()` removes whitespace. If nothing is left, the file is empty or only spaces. An empty file has no name line, so it is rejected.

**Line 199** `flash("File " + file.filename + " was rejected: the file is empty.")`

Explains which file and why.

**Line 200** `continue`

Skips the save and moves to the next file. This `continue` is inside `try`, which is allowed.

**Line 201** `name = resume_text.strip().split("\n")[0].strip()`

Same name rule as the demo loader: the first non-empty line, trimmed. This is the candidate’s name.

**Line 202** `contact = find_contact(resume_text)`

First word containing `@`, or `not found`.

**Line 203** `save_candidate(name, contact, resume_text)`

Writes the row, or replaces an existing candidate with the same name.

**Line 204** `saved_count = saved_count + 1`

One more successful save.

**Line 205** `except Exception:`

Runs if anything inside `try` raised an error, for example a file that cannot be read. `Exception` is the general error type. The program does not crash; it shows a message.

**Line 206** `flash("File " + file.filename + " could not be read.")`

Tells the user that this one file failed.

**Line 207** *(blank)*

Separates the loop from the summary message. After the loop, every file has been accepted, rejected, or reported.

**Line 208** `if saved_count > 0:`

Shows the success message only when at least one file was stored. If every file was rejected, the rejection messages are enough.

**Line 209** `flash(str(saved_count) + " file(s) uploaded.")`

`str` turns the number into text so it can be joined. The “(s)” covers both one file and many files without an extra if.

**Line 210** `return redirect(url_for("dashboard"))`

Always returns to the dashboard. Uploaded people appear under “Not scored yet” until Process is clicked, because `save_candidate` does not write a Match row.

**Line 211** *(blank)*

Separates the upload page from the keyword helpers.

## Lines 212–222 — keyword helpers

**Line 212** `def keyword_exists(job, keyword):`

Returns True if this keyword is already in one of the five slots. Capital letters are ignored.

**Line 213** `for existing in get_keyword_list(job):`

Loops over the filled keywords only. Empty slots are already excluded.

**Line 214** `if existing.lower() == keyword.lower():`

Compares lowercase copies. `Python` and `python` count as the same keyword, so a duplicate is blocked.

**Line 215** `return True`

Found a duplicate. The function stops.

**Line 216** `return False`

The loop finished with no match, so the keyword is new.

**Line 217** *(blank)*

Separates the two helpers.

**Line 218** `def set_keyword_slot(job, slot, keyword):`

Writes one slot. `keyword` can be a word or `""` when the slot is being cleared. `slot` is 1 to 5.

**Line 219** `db = get_db()`

Opens the database.

**Line 220** `db.execute("UPDATE Job SET keyword" + str(slot) + " = ? WHERE job_id = ?", (keyword, job["job_id"]))`

Builds the column name from the slot number. If `slot` is 3, the SQL becomes `UPDATE Job SET keyword3 = ? WHERE job_id = ?`. The keyword text itself stays in the `?`, so a keyword like `SQL` cannot change the command. The slot number is safe to concatenate because it came from `int(...)` on the form, and the loops only use 1 to 5. The job id in the `WHERE` clause stops the update from touching any other job.

**Say this:** “The column name has to be built from the slot number, because SQL cannot use a placeholder for a column name. The keyword text still goes through a question mark.”

**Line 221** `db.commit()`

Saves the change.

**Line 222** `db.close()`

Closes the connection.

**Line 223** *(blank)*

Separates helpers from the keyword pages.

## Lines 224–244 — add a keyword

**Line 224** `@app.route("/add_keyword", methods=["POST"])`

The Add keyword button submits here. POST only.

**Line 225** `def add_keyword():`

Handles that button.

**Line 226** `if not is_logged_in():`

Login guard.

**Line 227** `return redirect(url_for("login"))`

Back to login if the guard fails.

**Line 228** *(blank)*

Separates the guard from the form data.

**Line 229** `keyword = request.form["keyword"].strip()`

Reads the text box named `keyword` and removes surrounding spaces. The HTML `name` must match this string.

**Line 230** `job = get_job()`

Loads the current five slots so the program can see what is empty and what is already used.

**Line 231** *(blank)*

Separates loading from the three checks.

**Line 232** `if keyword == "":`

The box was empty, or only spaces, because `strip` already ran.

**Line 233** `flash("Keyword cannot be empty.")`

The error message. There is no `return` here. The function still reaches line 244, which redirects. That is fine, because the other branches are `elif` and `else`, so they will not also run.

**Line 234** `elif keyword_exists(job, keyword):`

`elif` means “else if”: this is checked only when the keyword was not empty. It blocks duplicates, ignoring capitals.

**Line 235** `flash("Keyword '" + keyword + "' is already in the list.")`

Quotes are included in the message so the word is visible. The quote characters are ordinary text inside the string.

**Line 236** `elif len(get_keyword_list(job)) >= MAX_KEYWORDS:`

Third check: five keywords are already stored. `>=` means “greater than or equal”. With a maximum of 5, this is the sixth keyword. This is the success-criteria limit.

**Line 237** `flash("You can only have " + str(MAX_KEYWORDS) + " keywords. Delete one first.")`

Tells the user the limit and what to do. `str` is required to join the number into the sentence.

**Line 238** `else:`

The keyword is non-empty, not a duplicate, and there is a free slot.

**Line 239** `for slot in range(1, MAX_KEYWORDS + 1):`

Walks slots 1 to 5 in order to find the first hole. Adding does not always use slot 1, because slot 1 might already be filled.

**Line 240** `if job["keyword" + str(slot)] == "":`

This slot is empty.

**Line 241** `set_keyword_slot(job, slot, keyword)`

Writes the keyword into that slot.

**Line 242** `break`

Stops the loop. Without `break`, a bug could fill every empty slot with the same word. `break` exits only the `for` loop, not the function.

**Say this:** “I put the new keyword in the first empty slot, then I break so it is written only once.”

**Line 243** `flash("Keyword '" + keyword + "' added.")`

Success message. This line is inside the `else`, so it does not run when a check failed. It is outside the `for`, but still inside the `else`, so it runs after the loop, including after `break`.

**Line 244** `return redirect(url_for("dashboard"))`

Every path ends here: error or success. The dashboard is drawn from the database, so the new keyword appears in the table.

**Line 245** *(blank)*

Separates routes.

## Lines 246–262 — edit a keyword

**Line 246** `@app.route("/edit_keyword", methods=["POST"])`

The Save button next to an existing keyword. POST only.

**Line 247** `def edit_keyword():`

Handles that button.

**Line 248** `if not is_logged_in():`

Login guard.

**Line 249** `return redirect(url_for("login"))`

Back to login if needed.

**Line 250** *(blank)*

Separates the guard from the inputs.

**Line 251** `slot = int(request.form["slot"])`

The form sends a hidden field named `slot`, for example `2`. `int` turns the text `"2"` into the number `2`, because later it is used as a number. The hidden field is how the server knows which row the Save button belongs to. The page can show five Save buttons; each one carries its own slot number.

**Line 252** `new_keyword = request.form["keyword"].strip()`

The edited text from that row’s text box.

**Line 253** `job = get_job()`

The current keywords, used to compare with what is already stored.

**Line 254** *(blank)*

Separates inputs from checks.

**Line 255** `if new_keyword == "":`

Empty after trimming is rejected. Save is not the Delete button. Clearing a slot is a separate action.

**Line 256** `flash("Keyword cannot be empty.")`

The message for that case.

**Line 257** `elif new_keyword.lower() != job["keyword" + str(slot)].lower() and keyword_exists(job, new_keyword):`

This is the duplicate rule for editing, and it is more careful than add.

- `new_keyword.lower() != job["keyword" + str(slot)].lower()` is true when the text actually changed, ignoring capitals.
- `keyword_exists(...)` is true when the new text is already in some slot.
- `and` means both must be true.

If the user opens slot 2, which is `Flask`, and presses Save without a real change, `keyword_exists` is true, but the first comparison is false, so the `and` is false and the save is allowed. If they change `Flask` to `Python` and `Python` is already in another slot, both parts are true and it is rejected. Changing `Flask` to `flask` is allowed, because ignoring capitals it is the same slot’s own word.

**Say this:** “Editing is allowed to keep the same word. It is not allowed to change a slot into a word that another slot already has.”

**Line 258** `flash("Keyword '" + new_keyword + "' is already in the list.")`

Duplicate message.

**Line 259** `else:`

Either the same word was saved again, or it is a genuinely new word.

**Line 260** `set_keyword_slot(job, slot, new_keyword)`

Overwrites that one column.

**Line 261** `flash("Keyword updated to '" + new_keyword + "'.")`

Confirms the new text. Old scores are not deleted here. The leaderboard still shows the previous Process until the user clicks Process again. If the teacher asks, say that the score is only recalculated on Process, so the user can see that they must press Process after changing keywords.

**Line 262** `return redirect(url_for("dashboard"))`

Back to the dashboard in every case.

**Line 263** *(blank)*

Separates routes.

## Lines 264–273 — delete a keyword

**Line 264** `@app.route("/delete_keyword", methods=["POST"])`

The Delete button next to a keyword. POST only. A link was not used, because deleting data should be a form submission, not a simple page visit.

**Line 265** `def delete_keyword():`

Handles that button.

**Line 266** `if not is_logged_in():`

Login guard.

**Line 267** `return redirect(url_for("login"))`

Back to login if needed.

**Line 268** *(blank)*

Separates the guard from the action.

**Line 269** `slot = int(request.form["slot"])`

Reads which slot to clear, the same hidden-field idea as Save.

**Line 270** `job = get_job()`

Needed because `set_keyword_slot` uses `job["job_id"]`.

**Line 271** `set_keyword_slot(job, slot, "")`

Writes an empty string into that column. The other keywords stay where they are. The list on the page hides empty slots, so the row disappears. The slot number itself is not renumbered; if slot 2 is cleared, the next added keyword can reuse slot 2 because add searches for the first empty slot.

**Line 272** `flash("Keyword deleted.")`

Confirms the deletion.

**Line 273** `return redirect(url_for("dashboard"))`

Back to the dashboard.

**Line 274** *(blank)*

Separates routes.

## Lines 275–287 — remove a candidate

**Line 275** `@app.route("/remove_candidate", methods=["POST"])`

The Remove button on a candidate row. POST only.

**Line 276** `def remove_candidate():`

Handles that button. This exists so a tester can clear the list and then press Process with no candidates.

**Line 277** `if not is_logged_in():`

Login guard.

**Line 278** `return redirect(url_for("login"))`

Back to login if needed.

**Line 279** *(blank)*

Separates the guard from the delete.

**Line 280** `cand_id = int(request.form["cand_id"])`

The hidden field identifies the candidate. `int` converts it from form text to a number.

**Line 281** `db = get_db()`

Opens the database.

**Line 282** `db.execute("DELETE FROM Match WHERE cand_id = ?", (cand_id,))`

Deletes any score for this candidate first. If the candidate row were deleted and the Match row were left, the database would contain a score for a person who no longer exists. The tables do not declare a foreign-key rule, so the program itself keeps that order.

**Say this:** “I delete the score first, then the person. The link is enforced by my code. I did not add a database foreign-key clause.”

**Line 283** `db.execute("DELETE FROM Candidate WHERE cand_id = ? AND user_id = ?", (cand_id, session["user_id"]))`

Deletes the candidate only if that id belongs to the logged-in user. The extra `user_id` check means a crafted form cannot delete someone else’s candidate. Then the row is gone: name, contact, and resume text.

**Line 284** `db.commit()`

Saves both deletes. They succeed or stay pending together until this line.

**Line 285** `db.close()`

Closes the connection.

**Line 286** `flash("Candidate removed.")`

Confirms it.

**Line 287** `return redirect(url_for("dashboard"))`

The row disappears because the page is rebuilt from the database.

**Line 288** *(blank)*

Separates routes.

## Lines 289–316 — Process

**Line 289** `@app.route("/process", methods=["POST"])`

The Process button. POST only.

**Line 290** `def process():`

Scores every candidate of this user against the current keywords and stores the scores.

**Line 291** `if not is_logged_in():`

Login guard.

**Line 292** `return redirect(url_for("login"))`

Back to login if needed.

**Line 293** *(blank)*

Separates the guard from the work.

**Line 294** `job = get_job()`

The job row, for its id and its keywords.

**Line 295** `keyword_list = get_keyword_list(job)`

The filled keywords only, for example `["Python", "Flask", "SQL", "Communication", "Teamwork"]`.

**Line 296** `db = get_db()`

Opens the database. It stays open until line 315, including when the function takes an early message path. That is why `db.close()` is outside the if/else, so it runs in every case.

**Line 297** `candidates = db.execute("SELECT * FROM Candidate WHERE user_id = ?", (session["user_id"],)).fetchall()`

All candidates for this user. Order does not matter here, because the dashboard sorts later.

**Line 298** *(blank)*

Separates loading from the two “cannot process” checks.

**Line 299** `if len(candidates) == 0:`

No rows. This is test T-12. The program must show a message and must not crash.

**Line 300** `flash("No candidates to process. Upload some .txt files first.")`

Explains what is missing.

**Line 301** `elif len(keyword_list) == 0:`

There are candidates, but every keyword slot is empty. Scoring against no keywords would give everyone 0, which would look like a real result. The program refuses instead.

**Line 302** `flash("No keywords to match. Add at least one keyword first.")`

Explains what is missing.

**Line 303** `else:`

Both lists have something in them. Scoring can run.

**Line 304** `try:`

Protects the database writes. The matching `except` is line 312. This is the database try/except from Criterion B.

**Line 305** `db.execute("DELETE FROM Match WHERE job_id = ?", (job["job_id"],))`

Deletes old scores for this job before writing new ones. Otherwise each Process would add another score row for the same candidate. The dashboard reads one Match row per candidate; duplicates would make that lookup ambiguous.

**Say this:** “Process replaces the old scores. It deletes them first, then inserts one new row per candidate.”

**Line 306** `for candidate in candidates:`

One score per candidate.

**Line 307** `score = get_score(candidate["resume_text"], keyword_list)`

Calls the linear search. The full resume text and the keyword list go in. An integer comes back.

**Line 308** `db.execute("INSERT INTO Match (cand_id, job_id, match_score) VALUES (?, ?, ?)",`

Inserts one Match row. `match_id` is generated. A score of 0 is still inserted, so the person appears on the leaderboard at the bottom, not in “Not scored yet”.

**Line 309** `(candidate["cand_id"], job["job_id"], score))`

The three values: which candidate, which job, how many hits.

**Line 310** `db.commit()`

Saves the delete and all the inserts. If this line is not reached because an error happened, the `except` runs and the commit is skipped.

**Line 311** `flash(str(len(candidates)) + " candidate(s) processed.")`

For 12 candidates the message is `12 candidate(s) processed.`

**Line 312** `except sqlite3.Error:`

Catches database errors only, such as a locked or corrupt database file. It does not catch every possible Python error. `sqlite3.Error` is the parent type for SQLite failures.

**Line 313** `flash("A database error happened while saving the scores.")`

The user sees a message instead of a crash page. Scores from this attempt are not committed.

**Line 314** *(blank)*

Ends the if/else visually before the shared cleanup.

**Line 315** `db.close()`

Runs whether Process scored people, refused, or caught a database error. The connection opened on line 296 is always closed.

**Line 316** `return redirect(url_for("dashboard"))`

The dashboard reads Match, bubble-sorts, and draws the leaderboard. Process itself does not sort. Sorting is a display step.

**Say this:** “Process only calculates and stores scores. The dashboard sorts them when it draws the page. After a refresh the scores are still there, because they are in the Match table.”

**Line 317** *(blank)*

Separates the pages from the startup lines.

## Lines 318–321 — start

**Line 318** `init_db()`

Runs as soon as Python loads this file. It is not inside a function, so it is not waiting to be called. Starting the program, or importing it on the server, creates the tables and the HR account if they are missing.

**Say this:** “This call is at the bottom on purpose. All the functions above exist before the database is initialised.”

**Line 319** *(blank)*

Separates setup from the local run check.

**Line 320** `if __name__ == "__main__":`

`__name__` is the string `"__main__"` only when this file was started directly, for example `python app.py`. If another program imports this file, `__name__` is `"app"` and this test is false. The hosted demo imports the file and starts it with its own server, so it should not also call `app.run`.

**Line 321** `app.run(debug=True, host="0.0.0.0", port=5000)`

Starts Flask’s development server.

- `debug=True` reloads code after a change and shows a detailed error in the browser if a page crashes. That is helpful while building. It is not how a finished public site should run.
- `host="0.0.0.0"` means “listen on every network address of this machine”, not only localhost. GitHub Codespaces needs this so the browser can reach the program.
- `port=5000` is the port in `http://localhost:5000`.

**Say this:** “The last line starts the website on port 5000. It only runs when I start the file myself.”

---

# File: templates/login.html

This file is HTML, plus a few Jinja tags. Jinja is Flask’s template language. `{{ something }}` prints a value. `{% something %}` is a command, such as a loop. Flask runs those tags on the server before the browser sees the page. The browser receives normal HTML.

**Line 1** `<!DOCTYPE html>`

Tells the browser “this is a modern HTML document”. It is not a visible element.

**Line 2** `<html>`

Opens the root element. Everything else is inside it. It is closed on line 27.

**Line 3** `<head>`

Opens the head. The head is information about the page, not the visible body. It is closed on line 6.

**Line 4** `<title>Candidate Matcher - Login</title>`

The text on the browser tab. The user does not see it inside the page box.

**Line 5** `<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">`

Links the CSS file. `rel="stylesheet"` means “this file describes appearance”. `url_for(...)` becomes an address such as `/static/style.css`. Using `url_for` is safer than typing the path, because Flask knows where static files are served from.

**Say this:** “The page does not contain the colours. It points at `style.css`.”

**Line 6** `</head>`

Closes the head.

**Line 7** `<body>`

Opens the visible page. Closed on line 26.

**Line 8** `<div class="box login-box">`

A `div` is a box. `class` is a label that CSS uses. This box has two classes: `box` gives the white card, and `login-box` makes it narrow and pushes it down the page.

**Line 9** `<h1>Candidate Matcher</h1>`

A top-level heading. `h1` is the largest heading tag used here.

**Line 10** `<p>Please log in to continue.</p>`

A paragraph of instructions. `p` means paragraph.

**Line 11** *(blank)*

Visual space in the file only. It does not create a gap on the page by itself. CSS controls the gaps.

**Line 12** `{% for message in get_flashed_messages() %}`

A Jinja loop. `get_flashed_messages()` returns the messages stored by `flash(...)` and then clears them. If login failed, this loop runs once per message. If there is no message, the loop body is skipped. After a refresh, the message is gone, because it was cleared when it was shown.

**Say this:** “Flash messages are one-time. The template loops over them and prints each one.”

**Line 13** `<p class="message">{{ message }}</p>`

Prints one message inside a paragraph. The class `message` makes the yellow warning box. `{{ message }}` inserts the text. Jinja escapes it, so a message cannot inject HTML.

**Line 14** `{% endfor %}`

Ends the `for` loop that started on line 12. Every Jinja `for` needs an `endfor`.

**Line 15** *(blank)*

Separates the messages from the form.

**Line 16** `<form method="post" action="{{ url_for('login') }}">`

Opens the form.

- `method="post"` sends the email and password in the request body, not in the address bar. A GET form would put the password in the URL, which would be wrong.
- `action` is where the form is sent. `url_for('login')` becomes `/login`, which is the Python function `login`.

**Line 17** `<label>Email</label>`

Visible text “Email”. It is not the input itself. It tells the user what to type.

**Line 18** `<input type="text" name="email">`

A one-line text box. `name="email"` is the key Python reads with `request.form["email"]`. The visible label and the `name` are different things. The `name` is what the program depends on.

**Line 19** *(blank)*

Separates the two fields in the file.

**Line 20** `<label>Password</label>`

Visible text “Password”.

**Line 21** `<input type="password" name="password">`

A password box. `type="password"` makes the browser show dots instead of characters. The value is still sent to the server. `name="password"` matches `request.form["password"]`.

**Line 22** *(blank)*

Separates the fields from the button.

**Line 23** `<button type="submit">Login</button>`

`type="submit"` means pressing this button sends the form. The visible word is Login.

**Line 24** `</form>`

Closes the form. Inputs after this would not be sent.

**Line 25** `</div>`

Closes the card opened on line 8.

**Line 26** `</body>`

Closes the body.

**Line 27** `</html>`

Closes the document opened on line 2.

---

# File: templates/dashboard.html

**Line 1** `<!DOCTYPE html>`

Same document type as the login page. Each template is a full page, not a fragment. There is no shared layout file.

**Line 2** `<html>`

Opens the document.

**Line 3** `<head>`

Opens the head.

**Line 4** `<title>Candidate Matcher - Dashboard</title>`

Browser-tab title, so the user can tell this tab from the login tab.

**Line 5** `<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">`

Same stylesheet as login. Both pages share one CSS file.

**Line 6** `</head>`

Closes the head.

**Line 7** `<body>`

Opens the visible page.

**Line 8** `<div class="top-bar">`

The header strip. The CSS class `top-bar` places the title on the left and Logout on the right.

**Line 9** `<h1>Candidate Matcher</h1>`

Page title inside the strip.

**Line 10** `<a href="{{ url_for('logout') }}">Logout</a>`

A link, not a form. `a` means anchor. `href` is the destination. `url_for('logout')` becomes `/logout`, which calls the Python `logout` function. Because it is a link, the browser sends GET.

**Line 11** `</div>`

Closes the top bar.

**Line 12** *(blank)*

Separates the header from the messages.

**Line 13** `{% for message in get_flashed_messages() %}`

Same one-time message loop as login. Upload errors, keyword messages, and “candidate(s) processed” all appear here.

**Line 14** `<p class="message">{{ message }}</p>`

Prints one message in the yellow style.

**Line 15** `{% endfor %}`

Ends that loop.

**Line 16** *(blank)*

Separates messages from section 1.

**Line 17** `<div class="box">`

Opens the first white card: upload.

**Line 18** `<h2>1. Upload candidate files</h2>`

Section heading. `h2` is a second-level heading, under the page `h1`.

**Line 19** `<p>Select one or more .txt files. The first line of each file must be the candidate's name.</p>`

Instructions. The apostrophe in `candidate's` is an ordinary character in HTML text. This sentence tells the user the name rule so they do not have to read the Python.

**Line 20** `<form method="post" action="{{ url_for('upload') }}" enctype="multipart/form-data">`

The upload form.

- POST to the Python `upload` function.
- `enctype="multipart/form-data"` is required for files. Without it, the browser would send the file name and not the file contents, and `request.files` would not work.

**Say this:** “The encoding type is what allows a file, not just text, to be submitted.”

**Line 21** `<input type="file" name="files" accept=".txt" multiple>`

The file picker.

- `type="file"` opens the operating system’s file dialog.
- `name="files"` matches `request.files.getlist("files")`.
- `accept=".txt"` suggests text files in the dialog. It is only a hint. Python still rejects other types.
- `multiple` allows many files in one selection. That is how 10 or more CVs are uploaded together.

**Line 22** `<button type="submit">Upload</button>`

Sends the form.

**Line 23** `</form>`

Closes the upload form.

**Line 24** `</div>`

Closes the first card.

**Line 25** *(blank)*

Separates section 1 from section 2.

**Line 26** `<div class="box">`

Opens the keyword card.

**Line 27** `<h2>2. Job requirement keywords</h2>`

Section heading.

**Line 28** `<table>`

Starts a table. The rows are built by the loop below, not typed out five times.

**Line 29** `<tr>`

`tr` means table row. This first row is the header.

**Line 30** `<th>#</th>`

`th` means table header cell. The symbol `#` stands for the slot number.

**Line 31** `<th>Keyword</th>`

Column title for the word.

**Line 32** `<th>Actions</th>`

Column title for Delete.

**Line 33** `</tr>`

Ends the header row.

**Line 34** `{% for slot in range(1, 6) %}`

Jinja loop. `range(1, 6)` is 1, 2, 3, 4, 5, the same five slots as Python’s `range(1, MAX_KEYWORDS + 1)`. The template writes `6` directly because Jinja does not see the Python constant `MAX_KEYWORDS`. If the teacher asks, say the limit is 5 in both places: the Python constant and this range.

**Line 35** `{% set keyword = job["keyword" + slot|string] %}`

`{% set %}` creates a template variable. `slot|string` turns the number 1 into the text `"1"`, because Jinja will not add a number to a string with `+`. `"keyword" + "1"` is `"keyword1"`. `job` is the row passed in from `render_template`. Reading `job["keyword1"]` returns that column. Empty slots are `""`.

**Say this:** “The template builds the column name the same way Python does: keyword plus the slot number.”

**Line 36** `{% if keyword != "" %}`

Hides empty slots. A deleted keyword disappears from the table because its column is `""`.

**Line 37** `<tr>`

Starts a visible data row for one filled keyword.

**Line 38** `<td>{{ slot }}</td>`

`td` is a normal cell. `{{ slot }}` prints 1, 2, 3, 4, or 5.

**Line 39** `<td>`

Opens the keyword cell. The form sits inside the cell.

**Line 40** `<form method="post" action="{{ url_for('edit_keyword') }}" class="inline">`

A small form whose only job is the Save button for this row. `class="inline"` stops the form from forcing a line break, so the text box and the button sit side by side. The action is the Python `edit_keyword` function.

**Line 41** `<input type="hidden" name="slot" value="{{ slot }}">`

A hidden field. The user does not see it, but it is submitted. `name="slot"` matches `request.form["slot"]`. `value` is this row’s number. Without this, the server would not know which of the five Save buttons was pressed.

**Line 42** `<input type="text" name="keyword" value="{{ keyword }}">`

A text box pre-filled with the current keyword. The user can change it and press Save. `name="keyword"` matches `request.form["keyword"]` in `edit_keyword`.

**Line 43** `<button type="submit">Save</button>`

Submits only this row’s form.

**Line 44** `</form>`

Closes the Save form.

**Line 45** `</td>`

Closes the keyword cell.

**Line 46** `<td>`

Opens the actions cell.

**Line 47** `<form method="post" action="{{ url_for('delete_keyword') }}" class="inline">`

A second form, separate from Save. Delete must be its own form so pressing Delete does not also send the edited text as a save. The action is `delete_keyword`.

**Line 48** `<input type="hidden" name="slot" value="{{ slot }}">`

Tells Delete which slot to clear.

**Line 49** `<button type="submit" class="danger">Delete</button>`

Submits the delete form. `class="danger"` makes the button red in CSS, so it looks different from Save.

**Line 50** `</form>`

Closes the delete form.

**Line 51** `</td>`

Closes the actions cell.

**Line 52** `</tr>`

Ends this keyword row.

**Line 53** `{% endif %}`

Ends the `if keyword != ""` from line 36.

**Line 54** `{% endfor %}`

Ends the slot loop from line 34.

**Line 55** `</table>`

Closes the keyword table.

**Line 56** *(blank)*

Separates the table from the add form.

**Line 57** `<form method="post" action="{{ url_for('add_keyword') }}">`

The Add keyword form. It is outside the table so there is always one add box, even when all five rows are hidden because they are empty. No `enctype` is needed because this form sends text, not a file.

**Line 58** `<label>New keyword</label>`

Visible label.

**Line 59** `<input type="text" name="keyword" placeholder="e.g. Python">`

The text box. `placeholder` is grey hint text. It is not submitted if the user does not type anything. `name="keyword"` matches `add_keyword`.

**Line 60** `<button type="submit">Add keyword</button>`

Submits the new word.

**Line 61** `</form>`

Closes the add form.

**Line 62** `</div>`

Closes the keyword card.

**Line 63** *(blank)*

Separates section 2 from section 3.

**Line 64** `<div class="box">`

Opens the results card.

**Line 65** `<h2>3. Results</h2>`

Section heading.

**Line 66** `<form method="post" action="{{ url_for('process') }}">`

Process has no text fields. The form only exists to send a POST to the `process` function. An empty POST is enough, because Process reads the database, not the form.

**Line 67** `<button type="submit" class="big">Process</button>`

The button. `class="big"` makes it larger in CSS so it is the main action.

**Line 68** `</form>`

Closes the Process form.

**Line 69** *(blank)*

Separates the button from the leaderboard.

**Line 70** `<h3>Leaderboard</h3>`

A third-level heading.

**Line 71** `{% if leaderboard|length == 0 %}`

`leaderboard` is the sorted list from Python. `|length` is Jinja’s length filter. Zero means nobody has been scored yet, or every scored person was removed.

**Line 72** `<p>No scores yet. Upload files, add keywords and click Process.</p>`

The empty-state sentence. It is shown instead of an empty table.

**Line 73** `{% else %}`

There is at least one scored candidate.

**Line 74** `<table>`

Starts the leaderboard table.

**Line 75** `<tr>`

Header row.

**Line 76** `<th>Rank</th>`

Column for 1, 2, 3, and so on.

**Line 77** `<th>Name</th>`

Column for the candidate name.

**Line 78** `<th>Contact</th>`

Column for the email or “not found”.

**Line 79** `<th>Match score</th>`

Column for the integer score.

**Line 80** `<th></th>`

An empty header for the Remove column. The cell exists so the columns line up. The header text is blank on purpose.

**Line 81** `</tr>`

Ends the header row.

**Line 82** `{% for candidate in leaderboard %}`

Loops in sorted order. Python already bubble-sorted this list, so the template does not sort. The first item is the highest score.

**Line 83** `{% if loop.index <= 3 %}`

`loop.index` is Jinja’s counter. It starts at 1, not 0. `<= 3` is ranks 1, 2, and 3. Those rows are highlighted. Rank 4 and below are not.

**Say this:** “The rank is not stored in the database. It is the position after sorting. `loop.index` is that position, and it starts at 1.”

**Line 84** `<tr class="top-three">`

A row with the class that CSS paints green. Only the top three get this tag.

**Line 85** `{% else %}`

Rank 4 or lower.

**Line 86** `<tr>`

A normal row, no extra class, so no green background.

**Line 87** `{% endif %}`

Ends the rank test. The cells below belong to whichever `tr` was opened.

**Line 88** `<td>{{ loop.index }}</td>`

Prints the rank.

**Line 89** `<td>{{ candidate[1] }}</td>`

`candidate` is `[cand_id, name, contact, score]`. Index 1 is the name. Jinja indexes start at 0, same as Python.

**Line 90** `<td>{{ candidate[2] }}</td>`

Index 2 is the contact.

**Line 91** `<td>{{ candidate[3] }}</td>`

Index 3 is the match score. This is the same index bubble sort compared.

**Line 92** `<td>`

Opens the Remove cell.

**Line 93** `<form method="post" action="{{ url_for('remove_candidate') }}" class="inline">`

One remove form per row, so each button carries a different id.

**Line 94** `<input type="hidden" name="cand_id" value="{{ candidate[0] }}">`

Index 0 is `cand_id`. It is hidden, but it is submitted as `cand_id`, which Python reads in `remove_candidate`.

**Line 95** `<button type="submit" class="danger">Remove</button>`

Red Remove button.

**Line 96** `</form>`

Closes that row’s form.

**Line 97** `</td>`

Closes the cell.

**Line 98** `</tr>`

Ends the candidate row. This closing tag matches both possible opening `tr` tags, because only one of them was written.

**Line 99** `{% endfor %}`

Ends the leaderboard loop.

**Line 100** `</table>`

Closes the leaderboard table.

**Line 101** `{% endif %}`

Ends the “is the leaderboard empty?” test from line 71.

**Line 102** *(blank)*

Separates the leaderboard from the not-scored section.

**Line 103** `{% if unscored_list|length > 0 %}`

Shows the next block only when at least one candidate has no Match row. If everyone has been processed, this whole section is omitted, not shown empty.

**Line 104** `<h3>Not scored yet</h3>`

Heading for that group.

**Line 105** `<p>These candidates were uploaded after the last Process. Click Process again to score them.</p>`

Explains why they are not on the leaderboard.

**Line 106** `<table>`

A second table, so these people are not given ranks.

**Line 107** `<tr>`

Header row.

**Line 108** `<th>Name</th>`

Name column. There is no Rank column here.

**Line 109** `<th>Contact</th>`

Contact column.

**Line 110** `<th>Match score</th>`

The header still says Match score, but the cell below does not print a number.

**Line 111** `<th></th>`

Blank header for Remove.

**Line 112** `</tr>`

Ends the header.

**Line 113** `{% for candidate in unscored_list %}`

Loops over the unsorted, unscored people. Order is upload order, because the dashboard query used `ORDER BY cand_id` and this list was not bubble-sorted.

**Line 114** `<tr>`

A normal row. No `top-three` class, because there is no rank.

**Line 115** `<td>{{ candidate[1] }}</td>`

Name, index 1.

**Line 116** `<td>{{ candidate[2] }}</td>`

Contact, index 2.

**Line 117** `<td>not scored yet</td>`

Fixed text, not `candidate[3]`. The Python list does contain a placeholder 0, but printing 0 would look like a real score. The page says “not scored yet” instead.

**Say this:** “I deliberately do not print the zero. Zero would mean they were processed and matched nothing.”

**Line 118** `<td>`

Opens the Remove cell.

**Line 119** `<form method="post" action="{{ url_for('remove_candidate') }}" class="inline">`

Same remove action as the leaderboard. One Python function handles both tables.

**Line 120** `<input type="hidden" name="cand_id" value="{{ candidate[0] }}">`

The candidate id.

**Line 121** `<button type="submit" class="danger">Remove</button>`

Red Remove button.

**Line 122** `</form>`

Closes the form.

**Line 123** `</td>`

Closes the cell.

**Line 124** `</tr>`

Ends the row.

**Line 125** `{% endfor %}`

Ends the unscored loop.

**Line 126** `</table>`

Closes that table.

**Line 127** `{% endif %}`

Ends the “is there anyone unscored?” test.

**Line 128** `</div>`

Closes the results card.

**Line 129** `</body>`

Closes the body.

**Line 130** `</html>`

Closes the document.

---

# File: static/style.css

CSS is a list of rules. A rule is a selector, then braces, then properties. The selector chooses elements. Each property sets one visual detail. Nothing in this file calculates scores.

**Line 1** `body {`

Selects the whole page body, on both login and dashboard. The `{` opens the list of properties. It closes on line 7.

**Line 2** `font-family: Arial, sans-serif;`

Uses Arial. If Arial is missing, the browser uses any sans-serif font. The comma is a fallback list.

**Line 3** `background-color: #f4f6f8;`

Page background. `#f4f6f8` is a light grey written as a hex colour: red `f4`, green `f6`, blue `f8`.

**Line 4** `margin: 0;`

Removes the browser’s default outer gap around the body, so the spacing is controlled by `padding` instead.

**Line 5** `padding: 20px;`

Puts 20 pixels of space inside the page edge, so the content does not touch the window border. `px` means pixels.

**Line 6** `color: #222;`

Default text colour, a near-black. `#222` is shorthand for `#222222`.

**Line 7** `}`

Ends the `body` rule.

**Line 8** *(blank)*

Separates rules. It has no effect on the page.

**Line 9** `h1, h2, h3 {`

Selects all three heading levels. The comma means “or”. One rule styles every heading.

**Line 10** `margin-top: 0;`

Removes the default gap above headings. The cards already have padding, so an extra top margin would look uneven.

**Line 11** `}`

Ends the heading rule.

**Line 12** *(blank)*

Separates rules.

**Line 13** `.top-bar {`

The dot means class. This selects every element with `class="top-bar"`, which is the dashboard header.

**Line 14** `display: flex;`

Turns the header into a flex row. Its children, the title and the logout link, sit in a row and can be pushed apart.

**Line 15** `justify-content: space-between;`

Puts the first child on the left and the last child on the right, with the free space between them. That is why Logout sits at the right edge.

**Line 16** `align-items: center;`

Vertically centres the title and the link with each other.

**Line 17** `max-width: 900px;`

The bar never grows wider than 900 pixels, even on a very wide monitor. It matches the cards below.

**Line 18** `margin: 0 auto 20px auto;`

Four values, in order: top, right, bottom, left.

- top `0`
- right `auto` — the browser splits spare width equally, which centres the bar
- bottom `20px` — gap before the next card
- left `auto` — the other half of the centring

**Say this:** “`auto` on the left and right centres the bar. 900 pixels is the same width as the cards, so the page lines up.”

**Line 19** `}`

Ends the top-bar rule.

**Line 20** *(blank)*

Separates rules.

**Line 21** `.box {`

Every white card: login, upload, keywords, and results. They all use `class="box"`.

**Line 22** `background-color: white;`

The card is white, on the grey page.

**Line 23** `border: 1px solid #ddd;`

A one-pixel solid light-grey border. Three values: width, style, colour.

**Line 24** `border-radius: 6px;`

Rounds the corners by 6 pixels.

**Line 25** `padding: 20px;`

Space inside the card, between the border and the text.

**Line 26** `max-width: 900px;`

Same width limit as the top bar.

**Line 27** `margin: 0 auto 20px auto;`

Centres the card and leaves 20 pixels under it. The next card starts after that gap.

**Line 28** `}`

Ends the box rule.

**Line 29** *(blank)*

Separates rules.

**Line 30** `.login-box {`

Extra rules for the login card only. It also has class `box`, so both rules apply. This rule only changes what is listed here.

**Line 31** `max-width: 350px;`

Overrides the 900-pixel width from `.box`. The login card is narrower because it holds only two fields. When two rules set the same property, the more specific class still applies because both are single classes; the one that comes later in the file wins. `.login-box` comes after `.box`, so 350 wins on the login page.

**Say this:** “The login card uses both classes. The later rule overrides the width.”

**Line 32** `margin-top: 80px;`

Pushes the login card down from the top so it sits in the middle area of the window instead of stuck to the top.

**Line 33** `}`

Ends the login-box rule. The other margins still come from `.box`.

**Line 34** *(blank)*

Separates rules.

**Line 35** `label {`

Selects every `label` element: Email, Password, and New keyword.

**Line 36** `display: block;`

`block` puts each label on its own line, above the input, instead of beside it.

**Line 37** `margin-top: 10px;`

A small gap above the label, so it does not collide with the previous field.

**Line 38** `font-weight: bold;`

Makes the label text bold.

**Line 39** `}`

Ends the label rule.

**Line 40** *(blank)*

Separates rules.

**Line 41** `input[type="text"],`

Selects text inputs only. The square brackets are an attribute selector: the input whose `type` is `text`. The comma means the rule continues onto the next selector. Keyword boxes and the login email box are included. The file input is not, because its type is `file`.

**Line 42** `input[type="password"] {`

Also selects the password box. The `{` opens the shared rule for both selectors.

**Line 43** `padding: 6px;`

Space inside the box around the typed text.

**Line 44** `border: 1px solid #bbb;`

A one-pixel mid-grey border so the box is visible on the white card.

**Line 45** `border-radius: 4px;`

Slightly rounded corners, a little less than the cards.

**Line 46** `width: 250px;`

The box is 250 pixels wide, wide enough for an email.

**Line 47** `}`

Ends the input rule.

**Line 48** *(blank)*

Separates rules.

**Line 49** `button {`

Every button: Login, Upload, Save, Delete, Add keyword, Process, Remove. Later rules override some of these properties for red and large buttons.

**Line 50** `padding: 6px 14px;`

Two values: 6 pixels top and bottom, 14 pixels left and right. The button is wider than it is tall.

**Line 51** `border: none;`

Removes the default grey border.

**Line 52** `border-radius: 4px;`

Rounds the button corners.

**Line 53** `background-color: #2d6cdf;`

Blue background. Hex `2d` red, `6c` green, `df` blue, so it looks blue.

**Line 54** `color: white;`

White text on that blue.

**Line 55** `cursor: pointer;`

The mouse pointer becomes a hand over the button, which signals that it can be clicked.

**Line 56** `margin-top: 6px;`

A small gap above the button so it does not stick to the input.

**Line 57** `}`

Ends the button rule.

**Line 58** *(blank)*

Separates rules.

**Line 59** `button.danger {`

Selects a `button` that also has class `danger`. This is more specific than `button` alone, so it overrides the blue background. Delete and Remove use this class.

**Line 60** `background-color: #c0392b;`

Red. The text stays white because this rule does not change `color`, so the white from the general button rule remains.

**Line 61** `}`

Ends the danger rule.

**Line 62** *(blank)*

Separates rules.

**Line 63** `button.big {`

The Process button, which has `class="big"`.

**Line 64** `font-size: 18px;`

Larger text than the other buttons. The browser default is about 16 pixels.

**Line 65** `padding: 10px 30px;`

More padding, so the button is physically bigger, not only the letters.

**Line 66** `}`

Ends the big-button rule. It stays blue because this rule does not set a background.

**Line 67** *(blank)*

Separates rules.

**Line 68** `form.inline {`

A `form` with class `inline`: the Save form, the Delete form, and the Remove forms.

**Line 69** `display: inline;`

A form is normally a block and starts on a new line. `inline` lets it sit inside the table cell next to other content. That is why the text box and Save appear on one line.

**Line 70** `}`

Ends the inline-form rule.

**Line 71** *(blank)*

Separates rules.

**Line 72** `.message {`

The flash-message paragraphs.

**Line 73** `max-width: 900px;`

Lines up with the cards.

**Line 74** `margin: 0 auto 15px auto;`

Centres the message and leaves 15 pixels below it.

**Line 75** `padding: 10px;`

Space inside the yellow box.

**Line 76** `background-color: #fff3cd;`

Pale yellow, the usual colour for a notice that is not a crash.

**Line 77** `border: 1px solid #f0d27a;`

A slightly darker yellow border.

**Line 78** `border-radius: 4px;`

Rounded corners.

**Line 79** `}`

Ends the message rule.

**Line 80** *(blank)*

Separates rules.

**Line 81** `table {`

Every table: keywords, leaderboard, and not-scored.

**Line 82** `border-collapse: collapse;`

By default, table cells have separate borders and a gap, which looks like a double line. `collapse` merges neighbouring borders into one line.

**Line 83** `width: 100%;`

The table fills the card width. `100%` means “all of the parent”, not all of the screen. The parent is the card, which is at most 900 pixels.

**Line 84** `margin-bottom: 15px;`

Space under the table, before the next heading or form.

**Line 85** `}`

Ends the table rule.

**Line 86** *(blank)*

Separates rules.

**Line 87** `th, td {`

Header cells and normal cells share these properties.

**Line 88** `border: 1px solid #ddd;`

The grid lines.

**Line 89** `padding: 8px;`

Space inside each cell so the text does not touch the grid.

**Line 90** `text-align: left;`

Text starts at the left of the cell. Numbers are left-aligned too, which is acceptable for this short table.

**Line 91** `}`

Ends the cell rule.

**Line 92** *(blank)*

Separates rules.

**Line 93** `th {`

Header cells only. They already have the border and padding from the previous rule. This adds a background.

**Line 94** `background-color: #eef1f5;`

A light blue-grey header, different from the white body cells.

**Line 95** `}`

Ends the header rule.

**Line 96** *(blank)*

Separates rules.

**Line 97** `tr.top-three td {`

Selects `td` cells that are inside a `tr` with class `top-three`. The space means “inside”. Ranking rows 1 to 3 use that class in the HTML. Styling the `td` rather than the `tr` is more reliable, because some browsers do not paint a background on the row itself.

**Say this:** “The green is not decided in Python. Python sorts the list. The template adds the class for ranks 1 to 3. CSS paints those cells.”

**Line 98** `background-color: #d4f5d4;`

Light green.

**Line 99** `font-weight: bold;`

Bold text, so the top three are obvious even if the green is hard to see.

**Line 100** `}`

Ends the highlight rule. This is the last line of the stylesheet.

---

# File: requirements.txt

**Line 1** `Flask>=3.0`

This is not program logic. It tells the installer which library to download. `Flask` is the package. `>=3.0` means version 3.0 or any newer 3.x version. Installing Flask also installs its dependencies, including Werkzeug, which provides the password functions. `sqlite3` is not listed because it comes with Python.

**Say this:** “The only extra library I install is Flask. The database library is already in Python.”

---

# Questions the teacher is likely to ask

Use these as practice. The line numbers are in `app.py` unless another file is named.

**Why is the password not stored as `hr12345`?**
Line 35 hashes it before line 36 stores it. Line 130 checks the hash. The original password cannot be read back.

**Where is linear search?**
Lines 86 to 93. The outer loop walks every resume word. The inner loop compares that word with every keyword. Each hit adds 1.

**Where is bubble sort?**
Lines 95 to 104. Neighbours are compared. If the left score is smaller, they swap, so the largest score moves to the front. Index 3 is the score.

**Why not use Python’s sort?**
So the algorithm required by the flowchart is visible in the code, not hidden inside a library call.

**What happens if two candidates have the same score?**
Line 101 uses `<`, not `<=`. Equal scores are not swapped, so the one who was uploaded first stays ahead.

**Where are the five keywords stored?**
In the Job table, columns `keyword1` to `keyword5`, created on line 30. Empty slots are empty strings. Line 69 builds a list and skips the empty ones.

**Why does the top three turn green?**
`bubble_sort` orders the list. In `dashboard.html` lines 83 to 84, `loop.index <= 3` adds the class `top-three`. In `style.css` lines 97 to 99, that class is painted green and bold.

**What if the user uploads a PDF?**
`app.py` line 193 checks the file name. A non-txt file is rejected with a message, and `continue` moves on to the next file. The page does not crash.

**What if there are no candidates?**
`process`, line 299, flashes a message and does not enter the scoring loop.

**What if the same CV is uploaded twice?**
`save_candidate`, lines 169 to 177, finds the same name, updates that row, and deletes the old score.

**How does the program remember who is logged in?**
Line 134 stores `user_id` in the session. Line 8 signs that session with the secret key. Line 59 checks that the key exists. Logout on line 141 clears it.

**Does Process sort the candidates?**
No. Process writes scores. The dashboard calls `bubble_sort` on line 164 every time the page is drawn. After a refresh, the scores are read from Match and sorted again.

**What is a limitation of the score?**
Repeated words count every time, so keyword stuffing raises the score. A keyword with a space never matches, because comparison is word by word. Contact detection only finds the first `@` word, not a phone number.
