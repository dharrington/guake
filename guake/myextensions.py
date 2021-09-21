import re

from gi.repository import Gdk

from guake import globals

QUICK_OPEN_MATCHERS = [
    (
        "Python traceback",
        r"^\s*File\s\".*\",\sline\s[0-9]+",
        r"^\s*File\s\"(.*)\",\sline\s([0-9]+)",
        ["term_click.py", "$1", "$2"],
    ),
    (
        "Python pytest report",
        r"^\s.*\:\:[a-zA-Z0-9\_]+\s",
        r"^\s*(.*\:\:[a-zA-Z0-9\_]+)\s",
        ["term_click.py", "$1", "$2"],
    ),
    (
        "line starts by 'ERROR in Filename:line' pattern (GCC/make). File path should exists.",
        r"\s.\S[^\s\s].[a-zA-Z0-9\/\_\-\.\ ]+\.?[a-zA-Z0-9]+\:[0-9]+",
        r"\s.\S[^\s\s].(.*)\:([0-9]+)",
        ["term_click.py", "$1", "$2"],
    ),
    (
        "A file name, with line number",
        r"[a-zA-Z0-9\/\_\-\.]+:[0-9]+",
        r"([a-zA-Z0-9\/\_\-\.]+):([0-9]+)",
        ["term_click.py", "$1", "$2"],
    ),
    (
        "A file name, no line number.",
        r"[a-zA-Z0-9\/\_\-\.]+",
        r"([a-zA-Z0-9\/\_\-\.]+)",
        ["term_click.py", "$1"],
    ),
]

def find_regex_match_at_col(rx, text, col):
    for m in re.finditer(rx, text):
        if m.start() <= col < m.end():
            return m
    return None

def my_button_press_handler(term, _, event):
    if event.button == 1 and (event.get_state() & Gdk.ModifierType.CONTROL_MASK):
        line = int(event.y / term.get_char_height())
        text, attributes = term.get_text_range(line, 0, line, 999999, None, None)
        col = int(event.x / term.get_char_width())
        text_index = None
        for i, a in enumerate(attributes):
            if a.column == col:
                text_index = i
        if text_index is None:
            return False
        text, attributes = term.get_text_range(line, 0, line+2, 0, None, None)

        for mat in QUICK_OPEN_MATCHERS:
            m = find_regex_match_at_col(mat[1], text, col)
            if m:
                m2 = re.match(mat[2], m.group(0))
                if m2:
                    cmd = mat[3]
                    for i in range(len(cmd)):
                        # shouldn't allow recursive substitutions...
                        for gi in range(1, 10):
                            sub = ""
                            if gi <= len(m2.groups()):
                                sub = m2.group(gi)
                            if not sub:
                                sub = ""
                            cmd[i] = cmd[i].replace("$"+str(gi), sub)
                    term.feed_child(chr(27)+'c '+' '.join(cmd)+'\n')
                    return

def init():
    globals.QUICK_OPEN_MATCHERS = []
    globals.TERMINAL_MATCH_EXPRS = []


init()
