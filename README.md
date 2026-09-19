# CS-HR-IA — Candidate Matcher

A small website for an HR user. Log in, upload candidate `.txt` files saved from LinkedIn, enter up to five job keywords, click **Process**, and see the candidates ranked from the highest to the lowest match score. The top three are highlighted in green.

Built for the IB Computer Science SL Internal Assessment (Criterion D). The explanation of how every part works, plus the list of sources, is in [HOW_THE_CODE_WORKS.md](HOW_THE_CODE_WORKS.md).

## How to run

1. Install Python 3 (3.10 or newer).
2. Install Flask:

```bash
pip install -r requirements.txt
```

3. Start the program:

```bash
python app.py
```

4. Open http://localhost:5000 in Chrome.

The database file `matcher.db` is created automatically the first time the program runs. Deleting this file resets everything (candidates, keywords, scores) back to the start.

## Login

| Email | Password |
|-------|----------|
| `hr@gmail.com` | `hr12345` |

(`wrong123` is a wrong password, used in test T-02.)

## Sample files

- `sample_cvs/` — 12 candidate files. Line 1 is the candidate's name, the body contains an email and a list of skills.
- `sample_cvs/bad_files/` — `resume.pdf` (wrong file type) and `empty.txt` (empty file) for the rejection tests.

Suggested keywords for the demo: `Python`, `Flask`, `SQL`, `Communication`, `Teamwork`.

## Running on GitHub Codespaces

Run `python app.py` in the terminal. Codespaces will show a pop-up "Open in Browser" for port 5000. If it does not appear, open the **Ports** tab, find port 5000 and click the globe icon. The program already listens on all addresses (`host="0.0.0.0"`), which is the one setting Codespaces needs.
