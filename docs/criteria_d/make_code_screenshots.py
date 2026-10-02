#!/usr/bin/env python3
"""Render short code excerpts as dark IDE-style PNG screenshots for Criterion D.

Excerpts and line numbers match APPENDIX_SOURCE_CODE.txt (comment-free Appendix A).
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
APPENDIX = ROOT / "APPENDIX_SOURCE_CODE.txt"
OUT = Path(__file__).resolve().parent / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

BG = (30, 30, 30)
GUTTER = (45, 45, 45)
LINE_NUM = (120, 120, 120)
DEFAULT = (212, 212, 212)
KEYWORD = (86, 156, 214)
STRING = (206, 145, 120)
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


def has_python_comment(text):
    """True if # starts a comment outside string quotes."""
    in_single = False
    in_double = False
    for ch in text:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return True
    return False


def appendix_lines(start, end):
    """Return (line_number, text) pairs from APPENDIX_SOURCE_CODE.txt inclusive."""
    all_lines = APPENDIX.read_text(encoding="utf-8").splitlines()
    pairs = []
    for num in range(start, end + 1):
        text = all_lines[num - 1]
        if has_python_comment(text):
            raise ValueError(f"Comment in appendix line {num}: {text}")
        pairs.append((num, text))
    return pairs


def tokenize_line(line):
    tokens = []
    i = 0
    while i < len(line):
        ch = line[i]
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
            if tokens and tokens[-1][0].rstrip().endswith("def"):
                color = FUNC
            tokens.append((word, color))
            i = j
            continue
        tokens.append((ch, DEFAULT))
        i += 1
    return tokens


def render_snippet(filename, title, pairs):
    """pairs: list of (line_number, text). Empty text with line_number None = blank gap."""
    font = get_font(17)
    bold = get_font(15)
    pad_x = 16
    pad_y = 14
    line_h = 26
    gutter_w = 54
    visible = [text for _, text in pairs]
    max_chars = max((len(line) for line in visible), default=40)
    width = gutter_w + pad_x * 2 + max(560, max_chars * 10 + 40)
    height = pad_y * 2 + 28 + line_h * len(pairs) + 10

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, gutter_w, height], fill=GUTTER)
    draw.text((pad_x, 8), title, fill=(170, 170, 170), font=bold)

    y = pad_y + 24
    for num, line in pairs:
        if num is not None:
            num_s = str(num)
            draw.text(
                (gutter_w - 10 - draw.textlength(num_s, font=font), y),
                num_s,
                fill=LINE_NUM,
                font=font,
            )
        x = gutter_w + pad_x
        for text, color in tokenize_line(line):
            draw.text((x, y), text, fill=color, font=font)
            x += draw.textlength(text, font=font)
        y += line_h

    path = OUT / filename
    img.save(path)
    print("wrote", path)


# 1. Password hashing / login — appendix lines 39–40 and 134–138
render_snippet(
    "code_01_login_hash.png",
    "Appendix A — login / password hashing",
    appendix_lines(39, 40) + [(None, "")] + appendix_lines(134, 138),
)

# 2. File upload reading / validation — appendix lines 190–205
render_snippet(
    "code_02_file_upload.png",
    "Appendix A — file upload and validation",
    appendix_lines(190, 205),
)

# 3. Linear search scoring — appendix lines 90–97
render_snippet(
    "code_03_linear_search.png",
    "Appendix A — linear search scoring",
    appendix_lines(90, 97),
)

# 4. Bubble sort — appendix lines 99–108
render_snippet(
    "code_04_bubble_sort.png",
    "Appendix A — bubble sort ranking",
    appendix_lines(99, 108),
)

# 5. SQLite parameterised query — appendix lines 309–314
render_snippet(
    "code_05_sqlite.png",
    "Appendix A — SQLite parameterised query",
    appendix_lines(309, 314),
)

# 6. Error handling invalid data — appendix lines 126–128 and 303–306
render_snippet(
    "code_06_error_handling.png",
    "Appendix A — error handling for invalid data",
    appendix_lines(126, 128) + [(None, "")] + appendix_lines(303, 306),
)

print("done")
