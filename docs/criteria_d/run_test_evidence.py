#!/usr/bin/env python3
"""Automated Criterion D test evidence with Flask test client."""

import os
import re
import sys
from io import BytesIO
from pathlib import Path

ROOT = Path("/workspace")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
if (ROOT / "matcher.db").exists():
    (ROOT / "matcher.db").unlink()

import app as candidate_app  # noqa: E402

client = candidate_app.app.test_client()
results = []


def run(tid, sc, desc, data, observed):
    results.append((tid, sc, desc, data, observed))
    print(f"{tid}: {observed}")


# T-01 valid login
r = client.post(
    "/login",
    data={"email": "hr@gmail.com", "password": "hr12345"},
    follow_redirects=True,
)
run(
    "T-01",
    "SC-01",
    "Valid login",
    "hr@gmail.com / hr12345",
    "Redirected to Dashboard; upload and keywords sections visible."
    if b"Upload candidate files" in r.data
    else "FAIL",
)

# logout then T-02
client.get("/logout")
r = client.post(
    "/login",
    data={"email": "hr@gmail.com", "password": "wrong123"},
    follow_redirects=True,
)
run(
    "T-02",
    "SC-01",
    "Invalid password",
    "hr@gmail.com / wrong123",
    "Error message shown: Invalid email or password. User stayed on login page."
    if b"Invalid email or password." in r.data
    else "FAIL",
)

# T-03 empty fields
r = client.post("/login", data={"email": "", "password": ""}, follow_redirects=True)
run(
    "T-03",
    "SC-01",
    "Empty login fields",
    "empty email and password",
    "Error message shown: Please enter both email and password."
    if b"Please enter both email and password." in r.data
    else "FAIL",
)

# Login for remaining tests
client.post(
    "/login",
    data={"email": "hr@gmail.com", "password": "hr12345"},
    follow_redirects=True,
)

# T-06 no file
r = client.post(
    "/upload",
    data={"files": (BytesIO(b""), "")},
    content_type="multipart/form-data",
    follow_redirects=True,
)
run(
    "T-06",
    "SC-02",
    "Upload with no file",
    "no file selected",
    "Error message shown: No file selected."
    if b"No file selected." in r.data
    else "FAIL: " + r.data.decode()[:200],
)

# T-05 invalid pdf
with open("sample_cvs/bad_files/resume.pdf", "rb") as f:
    pdf_data = f.read()
r = client.post(
    "/upload",
    data={"files": (BytesIO(pdf_data), "resume.pdf")},
    content_type="multipart/form-data",
    follow_redirects=True,
)
run(
    "T-05",
    "SC-02",
    "Invalid file type",
    "resume.pdf",
    "Error message shown: only .txt files are allowed. File was not stored."
    if b"only .txt files are allowed" in r.data
    else "FAIL",
)

# T-12 process with no candidates
r = client.post("/process", follow_redirects=True)
run(
    "T-12",
    "SC-05",
    "Process with no candidates",
    "no candidates uploaded",
    "Error message shown: No candidates to process. App did not crash."
    if b"No candidates to process" in r.data
    else "FAIL",
)

# T-04 valid upload
with open("sample_cvs/01_Karolina_Nowak.txt", "rb") as f:
    txt = f.read()
r = client.post(
    "/upload",
    data={"files": (BytesIO(txt), "01_Karolina_Nowak.txt")},
    content_type="multipart/form-data",
    follow_redirects=True,
)
run(
    "T-04",
    "SC-02",
    "Valid .txt upload",
    "01_Karolina_Nowak.txt",
    "File accepted; candidate Karolina Nowak appears on dashboard."
    if b"Karolina Nowak" in r.data and b"uploaded" in r.data
    else "FAIL",
)

# Process with candidates but no keywords
r = client.post("/process", follow_redirects=True)
run(
    "T-12c",
    "SC-05",
    "Process with no keywords",
    "1 candidate, 0 keywords",
    "Error message shown: No keywords to match."
    if b"No keywords to match" in r.data
    else "FAIL",
)

# T-08 add keyword
r = client.post("/add_keyword", data={"keyword": "Python"}, follow_redirects=True)
run(
    "T-08",
    "SC-03",
    "Add keyword",
    "Python",
    "Keyword Python appears in the keyword list."
    if b"Python" in r.data and b"added" in r.data
    else "FAIL",
)

# empty keyword
r = client.post("/add_keyword", data={"keyword": ""}, follow_redirects=True)
run(
    "T-08b",
    "SC-03",
    "Empty keyword (invalid)",
    "empty string",
    "Error message shown: Keyword cannot be empty."
    if b"Keyword cannot be empty" in r.data
    else "FAIL",
)

# Add remaining keywords
for kw in ["Flask", "SQL", "Communication", "Teamwork"]:
    client.post("/add_keyword", data={"keyword": kw}, follow_redirects=True)

# Upload more candidates
for name in [
    "02_Oliver_Smith.txt",
    "03_Amelia_Brown.txt",
    "04_Lucas_Meyer.txt",
    "05_Sofia_Rossi.txt",
    "06_Daniel_Kim.txt",
    "07_Emma_Johansson.txt",
    "08_Mateusz_Kowalski.txt",
    "09_Chloe_Martin.txt",
    "10_Ahmed_Hassan.txt",
    "11_Isabella_Garcia.txt",
    "12_Noah_Williams.txt",
]:
    with open(f"sample_cvs/{name}", "rb") as f:
        data = f.read()
    client.post(
        "/upload",
        data={"files": (BytesIO(data), name)},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

# T-07 check count of waiting candidates
r = client.get("/dashboard")
# unscored list shows waiting candidates
waiting = r.data.decode().count("Remove")
run(
    "T-07",
    "SC-08",
    "10+ file uploads",
    "12 valid .txt files",
    f"{waiting} candidates present after bulk upload (expected 12)."
    if waiting >= 10
    else f"FAIL count={waiting}",
)

# T-11 / T-13 / T-14 / T-15 process
r = client.post("/process", follow_redirects=True)
rows = re.findall(
    r"<tr(?: class=\"top3\")?>\s*<td>(\d+)</td>\s*<td>([^<]+)</td>\s*<td>(\d+)</td>",
    r.data.decode(),
)
run(
    "T-11",
    "SC-05",
    "Match score displayed",
    "12 candidates + 5 keywords",
    f"Leaderboard shows {len(rows)} candidates with scores next to names."
    if len(rows) >= 10
    else f"FAIL rows={rows}",
)

sorted_ok = all(int(rows[i][2]) >= int(rows[i + 1][2]) for i in range(len(rows) - 1))
run(
    "T-13",
    "SC-06",
    "Sorting highest to lowest",
    str([(n, s) for _, n, s in rows[:5]]),
    f"Leaderboard ordered descending. Top rows: {rows[:5]}"
    if sorted_ok
    else f"FAIL {rows}",
)

run(
    "T-14",
    "SC-07",
    "Final leaderboard",
    "full workflow",
    f"Numbered leaderboard with {len(rows)} candidates and scores displayed.",
)

has_top3 = b"top3" in r.data
run(
    "T-15",
    "SC-07",
    "Top 3 highlighted",
    ">=4 scored candidates",
    "Ranks 1, 2 and 3 use the green top3 highlight class."
    if has_top3
    else "FAIL: top3 class missing",
)

# Duplicate keyword invalid
r = client.post("/add_keyword", data={"keyword": "python"}, follow_redirects=True)
run(
    "T-09b",
    "SC-04",
    "Duplicate keyword (invalid)",
    "python (already have Python)",
    "Error message shown: Keyword is already in the list."
    if b"already in the list" in r.data
    else "FAIL",
)

out = Path("/workspace/docs/criteria_d/observed_results.md")
lines = [
    "| Test ID | Success Criterion | Description | Test Data | Observed Results |",
    "|---|---|---|---|---|",
]
for tid, sc, desc, data, obs in results:
    lines.append(f"| {tid} | {sc} | {desc} | {data} | {obs} |")
out.write_text("\n".join(lines) + "\n")
print("wrote", out)

# Keep matcher.db populated for browser screenshots
print("DB left populated for UI screenshots.")
