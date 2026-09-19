# Candidate Matcher - IB Computer Science IA (Criterion D)
#
# One HR user logs in, uploads candidate .txt files, keeps up to five
# job keywords, and clicks Process. The program counts keyword matches
# in every resume (linear search), sorts the candidates with bubble sort,
# and shows a leaderboard with the top three highlighted.
#
# The overall shape (one file, SQLite, session login, templates) follows
# the official Flask tutorial: https://flask.palletsprojects.com/en/stable/tutorial/

import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# The secret key lets Flask remember who is logged in between pages.
app.secret_key = "ib-computer-science-ia-secret"

DATABASE_FILE = "matcher.db"
MAX_KEYWORDS = 5


# ---------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------

# Opens the database file and returns the connection.
# Rows can then be read by column name, e.g. row["name"].
def get_db():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


# Creates the four tables if they do not exist yet and adds the
# HR account plus one empty job. Runs once when the program starts.
def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS User (user_id INTEGER PRIMARY KEY, email TEXT, password_hash TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS Candidate (cand_id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, contact TEXT, resume_text TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS Job (job_id INTEGER PRIMARY KEY, user_id INTEGER, keyword1 TEXT, keyword2 TEXT, keyword3 TEXT, keyword4 TEXT, keyword5 TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS Match (match_id INTEGER PRIMARY KEY, cand_id INTEGER, job_id INTEGER, match_score INTEGER)")

    user = db.execute("SELECT * FROM User WHERE email = ?", ("hr@gmail.com",)).fetchone()
    if user is None:
        password_hash = generate_password_hash("hr12345")
        db.execute("INSERT INTO User (email, password_hash) VALUES (?, ?)", ("hr@gmail.com", password_hash))
        db.execute("INSERT INTO Job (user_id, keyword1, keyword2, keyword3, keyword4, keyword5) VALUES (1, '', '', '', '', '')")

    db.commit()
    db.close()


# Returns True if somebody is logged in, otherwise False.
def is_logged_in():
    if "user_id" in session:
        return True
    return False


# Returns the job row of the logged-in HR user.
# Every HR user has exactly one job (one set of five keywords).
def get_job():
    db = get_db()
    job = db.execute("SELECT * FROM Job WHERE user_id = ?", (session["user_id"],)).fetchone()
    db.close()
    return job


# Turns the five keyword columns of the job into a normal Python list.
# Empty slots are skipped, so the list only has real keywords.
def get_keyword_list(job):
    keyword_list = []
    for slot in range(1, MAX_KEYWORDS + 1):
        keyword = job["keyword" + str(slot)]
        if keyword != "":
            keyword_list.append(keyword)
    return keyword_list


# ---------------------------------------------------------------------
# The two algorithms: linear search scoring and bubble sort
# ---------------------------------------------------------------------

# Turns a block of text into a list of lower-case words.
# Punctuation is replaced by spaces so "Python," becomes "python".
def clean_words(text):
    cleaned = ""
    for character in text.lower():
        if character.isalnum():
            cleaned = cleaned + character
        else:
            cleaned = cleaned + " "
    return cleaned.split()


# Linear search: goes through the resume word by word and compares each
# word with each keyword. Every match adds 1 to the score.
def get_score(resume_text, keyword_list):
    words = clean_words(resume_text)
    score = 0
    for word in words:
        for keyword in keyword_list:
            if word == keyword.lower().strip():
                score = score + 1
    return score


# Bubble sort: compares neighbours and swaps them if the left score is
# lower than the right one, so the highest score ends up first.
# Each item in the list looks like [cand_id, name, contact, score].
def bubble_sort(candidate_list):
    n = len(candidate_list)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            left = candidate_list[j]
            right = candidate_list[j + 1]
            if left[3] < right[3]:
                candidate_list[j] = right
                candidate_list[j + 1] = left
    return candidate_list


# Looks for the first word that contains "@" and returns it as the
# contact. If there is no such word, returns "not found".
def find_contact(text):
    for word in text.split():
        if "@" in word:
            return word
    return "not found"


# ---------------------------------------------------------------------
# Pages: login and dashboard
# ---------------------------------------------------------------------

# The start page just sends the user to the login page.
@app.route("/")
def index():
    return redirect(url_for("login"))


# Login page. GET shows the form, POST checks email and password.
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        if email == "" or password == "":
            flash("Please enter both email and password.")
            return render_template("login.html")

        db = get_db()
        user = db.execute("SELECT * FROM User WHERE email = ?", (email,)).fetchone()
        db.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.")
            return render_template("login.html")

        session["user_id"] = user["user_id"]
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# Logs the user out by forgetting the session.
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# Dashboard: shows upload form, keyword slots and the leaderboard.
@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

    job = get_job()
    db = get_db()
    candidates = db.execute("SELECT * FROM Candidate WHERE user_id = ? ORDER BY cand_id", (session["user_id"],)).fetchall()

    scored_list = []
    unscored_list = []
    for candidate in candidates:
        match = db.execute("SELECT match_score FROM Match WHERE cand_id = ? AND job_id = ?",
                           (candidate["cand_id"], job["job_id"])).fetchone()
        if match is None:
            unscored_list.append([candidate["cand_id"], candidate["name"], candidate["contact"], 0])
        else:
            scored_list.append([candidate["cand_id"], candidate["name"], candidate["contact"], match["match_score"]])
    db.close()

    leaderboard = bubble_sort(scored_list)
    return render_template("dashboard.html", job=job, leaderboard=leaderboard, unscored_list=unscored_list)


# ---------------------------------------------------------------------
# Actions: upload, keywords, remove, process
# ---------------------------------------------------------------------

# Saves one candidate. If a candidate with the same name already exists
# for this HR user, the old record is replaced instead of duplicated.
def save_candidate(name, contact, resume_text):
    db = get_db()
    existing = db.execute("SELECT cand_id FROM Candidate WHERE user_id = ? AND name = ?",
                          (session["user_id"], name)).fetchone()
    if existing is None:
        db.execute("INSERT INTO Candidate (user_id, name, contact, resume_text) VALUES (?, ?, ?, ?)",
                   (session["user_id"], name, contact, resume_text))
    else:
        db.execute("UPDATE Candidate SET contact = ?, resume_text = ? WHERE cand_id = ?",
                   (contact, resume_text, existing["cand_id"]))
        db.execute("DELETE FROM Match WHERE cand_id = ?", (existing["cand_id"],))
    db.commit()
    db.close()


# Handles the Upload button. Accepts many .txt files at once,
# rejects wrong file types and empty files.
@app.route("/upload", methods=["POST"])
def upload():
    if not is_logged_in():
        return redirect(url_for("login"))

    files = request.files.getlist("files")
    if len(files) == 0 or files[0].filename == "":
        flash("No file selected.")
        return redirect(url_for("dashboard"))

    saved_count = 0
    for file in files:
        if not file.filename.lower().endswith(".txt"):
            flash("File " + file.filename + " was rejected: only .txt files are allowed.")
            continue
        try:
            resume_text = file.read().decode("utf-8", "ignore")
            if resume_text.strip() == "":
                flash("File " + file.filename + " was rejected: the file is empty.")
                continue
            name = resume_text.strip().split("\n")[0].strip()
            contact = find_contact(resume_text)
            save_candidate(name, contact, resume_text)
            saved_count = saved_count + 1
        except Exception:
            flash("File " + file.filename + " could not be read.")

    if saved_count > 0:
        flash(str(saved_count) + " file(s) uploaded.")
    return redirect(url_for("dashboard"))


# Returns True if the keyword is already in one of the five slots.
# Capital letters are ignored, so "python" and "Python" are the same.
def keyword_exists(job, keyword):
    for existing in get_keyword_list(job):
        if existing.lower() == keyword.lower():
            return True
    return False


# Writes a keyword (or an empty string) into one slot of the job.
def set_keyword_slot(job, slot, keyword):
    db = get_db()
    db.execute("UPDATE Job SET keyword" + str(slot) + " = ? WHERE job_id = ?", (keyword, job["job_id"]))
    db.commit()
    db.close()


# Handles the Add keyword button: puts the keyword in the first empty slot.
@app.route("/add_keyword", methods=["POST"])
def add_keyword():
    if not is_logged_in():
        return redirect(url_for("login"))

    keyword = request.form["keyword"].strip()
    job = get_job()

    if keyword == "":
        flash("Keyword cannot be empty.")
    elif keyword_exists(job, keyword):
        flash("Keyword '" + keyword + "' is already in the list.")
    elif len(get_keyword_list(job)) >= MAX_KEYWORDS:
        flash("You can only have " + str(MAX_KEYWORDS) + " keywords. Delete one first.")
    else:
        for slot in range(1, MAX_KEYWORDS + 1):
            if job["keyword" + str(slot)] == "":
                set_keyword_slot(job, slot, keyword)
                break
        flash("Keyword '" + keyword + "' added.")
    return redirect(url_for("dashboard"))


# Handles the Save button next to a keyword: changes the text in that slot.
@app.route("/edit_keyword", methods=["POST"])
def edit_keyword():
    if not is_logged_in():
        return redirect(url_for("login"))

    slot = int(request.form["slot"])
    new_keyword = request.form["keyword"].strip()
    job = get_job()

    if new_keyword == "":
        flash("Keyword cannot be empty.")
    elif new_keyword.lower() != job["keyword" + str(slot)].lower() and keyword_exists(job, new_keyword):
        flash("Keyword '" + new_keyword + "' is already in the list.")
    else:
        set_keyword_slot(job, slot, new_keyword)
        flash("Keyword updated to '" + new_keyword + "'.")
    return redirect(url_for("dashboard"))


# Handles the Delete button next to a keyword: empties that slot.
@app.route("/delete_keyword", methods=["POST"])
def delete_keyword():
    if not is_logged_in():
        return redirect(url_for("login"))

    slot = int(request.form["slot"])
    job = get_job()
    set_keyword_slot(job, slot, "")
    flash("Keyword deleted.")
    return redirect(url_for("dashboard"))


# Handles the Remove button next to a candidate.
@app.route("/remove_candidate", methods=["POST"])
def remove_candidate():
    if not is_logged_in():
        return redirect(url_for("login"))

    cand_id = int(request.form["cand_id"])
    db = get_db()
    db.execute("DELETE FROM Match WHERE cand_id = ?", (cand_id,))
    db.execute("DELETE FROM Candidate WHERE cand_id = ? AND user_id = ?", (cand_id, session["user_id"]))
    db.commit()
    db.close()
    flash("Candidate removed.")
    return redirect(url_for("dashboard"))


# Handles the Process button: scores every candidate against the
# keywords and stores the scores in the Match table.
@app.route("/process", methods=["POST"])
def process():
    if not is_logged_in():
        return redirect(url_for("login"))

    job = get_job()
    keyword_list = get_keyword_list(job)
    db = get_db()
    candidates = db.execute("SELECT * FROM Candidate WHERE user_id = ?", (session["user_id"],)).fetchall()

    if len(candidates) == 0:
        flash("No candidates to process. Upload some .txt files first.")
    elif len(keyword_list) == 0:
        flash("No keywords to match. Add at least one keyword first.")
    else:
        try:
            db.execute("DELETE FROM Match WHERE job_id = ?", (job["job_id"],))
            for candidate in candidates:
                score = get_score(candidate["resume_text"], keyword_list)
                db.execute("INSERT INTO Match (cand_id, job_id, match_score) VALUES (?, ?, ?)",
                           (candidate["cand_id"], job["job_id"], score))
            db.commit()
            flash(str(len(candidates)) + " candidate(s) processed.")
        except sqlite3.Error:
            flash("A database error happened while saving the scores.")

    db.close()
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------
# Start the program
# ---------------------------------------------------------------------

init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
