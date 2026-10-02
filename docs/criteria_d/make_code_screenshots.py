#!/usr/bin/env python3
"""Render short code excerpts as dark IDE-style PNG screenshots for Criterion D."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

BG = (30, 30, 30)
GUTTER = (45, 45, 45)
LINE_NUM = (120, 120, 120)
DEFAULT = (212, 212, 212)
KEYWORD = (86, 156, 214)
STRING = (206, 145, 120)
COMMENT = (106, 153, 85)
FUNC = (220, 220, 170)
NUMBER = (181, 206, 168)

KEYWORDS = {
    "def", "return", "for", "in", "if", "else", "elif", "or", "and", "not",
    "None", "True", "False", "import", "from", "as", "try", "except",
    "with", "range", "len", "str", "int", "continue",
}


def get_font(size=18):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def tokenize_line(line):
    """Very small highlighter good enough for Python excerpts."""
    tokens = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "#":
            tokens.append((line[i:], COMMENT))
            break
        if ch in "\"'":
            quote = ch
            j = i + 1
            while j < len(line) and line[j] != quote:
                j += 1
            j = min(j + 1, len(line))
            tokens.append((line[i:j], STRING))
            i = j
            continue
        if ch.isdigit():
            j = i
            while j < len(line) and (line[j].isdigit() or line[j] == "."):
                j += 1
            tokens.append((line[i:j], NUMBER))
            i = j
            continue
        if ch.isalpha() or ch == "_":
            j = i
            while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                j += 1
            word = line[i:j]
            color = KEYWORD if word in KEYWORDS else DEFAULT
            # Function name after def
            if tokens and tokens[-1][0].rstrip().endswith("def"):
                color = FUNC
            tokens.append((word, color))
            i = j
            continue
        tokens.append((ch, DEFAULT))
        i += 1
    return tokens


def render_snippet(filename, title, lines, start_line=1):
    font = get_font(17)
    bold = get_font(15)
    pad_x = 16
    pad_y = 14
    line_h = 26
    gutter_w = 54
    max_chars = max(len(line) for line in lines)
    width = gutter_w + pad_x * 2 + max(560, max_chars * 10 + 40)
    height = pad_y * 2 + 28 + line_h * len(lines) + 10

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, gutter_w, height], fill=GUTTER)
    draw.text((pad_x, 8), title, fill=(170, 170, 170), font=bold)

    y = pad_y + 24
    for idx, line in enumerate(lines):
        num = str(start_line + idx)
        draw.text((gutter_w - 10 - draw.textlength(num, font=font), y), num, fill=LINE_NUM, font=font)
        x = gutter_w + pad_x
        for text, color in tokenize_line(line):
            draw.text((x, y), text, fill=color, font=font)
            x += draw.textlength(text, font=font)
        y += line_h

    path = OUT / filename
    img.save(path)
    print("wrote", path)


# 1. Password hashing / login
render_snippet(
    "code_01_login_hash.png",
    "app.py — login / password hashing",
    [
        "password_hash = generate_password_hash(\"hr12345\")",
        "db.execute(\"INSERT INTO User (email, password_hash) VALUES (?, ?)\",",
        "           (\"hr@gmail.com\", password_hash))",
        "",
        "if user is None or not check_password_hash(user[\"password_hash\"], password):",
        "    flash(\"Invalid email or password.\")",
        "    return render_template(\"login.html\")",
        "session[\"user_id\"] = user[\"user_id\"]",
    ],
    start_line=66,
)

# 2. File upload reading / validation
render_snippet(
    "code_02_file_upload.png",
    "app.py — file upload and validation",
    [
        "files = request.files.getlist(\"files\")",
        "if len(files) == 0 or files[0].filename == \"\":",
        "    flash(\"No file selected.\")",
        "    return redirect(url_for(\"dashboard\"))",
        "for file in files:",
        "    if not file.filename.lower().endswith(\".txt\"):",
        "        flash(\"File \" + file.filename + \" was rejected: only .txt files are allowed.\")",
        "        continue",
        "    resume_text = file.read().decode(\"utf-8\", \"ignore\")",
        "    name = resume_text.strip().split(\"\\n\")[0].strip()",
    ],
    start_line=267,
)

# 3. Linear search scoring
render_snippet(
    "code_03_linear_search.png",
    "app.py — linear search scoring",
    [
        "def get_score(resume_text, keyword_list):",
        "    words = clean_words(resume_text)",
        "    score = 0",
        "    for word in words:                    # outer loop: every resume word",
        "        for keyword in keyword_list:      # inner loop: every keyword",
        "            if word == keyword.lower().strip():",
        "                score = score + 1         # match found → +1",
        "    return score",
    ],
    start_line=138,
)

# 4. Bubble sort
render_snippet(
    "code_04_bubble_sort.png",
    "app.py — bubble sort ranking",
    [
        "def bubble_sort(candidate_list):",
        "    n = len(candidate_list)",
        "    for i in range(n - 1):",
        "        for j in range(n - 1 - i):",
        "            left = candidate_list[j]",
        "            right = candidate_list[j + 1]",
        "            if left[3] < right[3]:       # compare match scores",
        "                candidate_list[j] = right",
        "                candidate_list[j + 1] = left",
        "    return candidate_list",
    ],
    start_line=151,
)

# 5. SQLite parameterised query / CRUD
render_snippet(
    "code_05_sqlite.png",
    "app.py — SQLite parameterised query",
    [
        "db.execute(\"DELETE FROM Match WHERE job_id = ?\", (job[\"job_id\"],))",
        "for candidate in candidates:",
        "    score = get_score(candidate[\"resume_text\"], keyword_list)",
        "    db.execute(",
        "        \"INSERT INTO Match (cand_id, job_id, match_score) VALUES (?, ?, ?)\",",
        "        (candidate[\"cand_id\"], job[\"job_id\"], score))",
        "db.commit()",
    ],
    start_line=402,
)

# 6. Error handling invalid data
render_snippet(
    "code_06_error_handling.png",
    "app.py — error handling for invalid data",
    [
        "if email == \"\" or password == \"\":",
        "    flash(\"Please enter both email and password.\")",
        "    return render_template(\"login.html\")",
        "",
        "if len(candidates) == 0:",
        "    flash(\"No candidates to process. Upload some .txt files first.\")",
        "elif len(keyword_list) == 0:",
        "    flash(\"No keywords to match. Add at least one keyword first.\")",
    ],
    start_line=189,
)

print("done")
