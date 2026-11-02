#!/usr/bin/env python3
"""Western Heart clean QuickBMS script linter.

QuickBMS itself ships no 64-bit Linux build (the 32-bit binary is
reported to segfault on x86_64 Linux), so on this platform scripts are
validated statically instead of executed. This linter checks:

1. Block commands are balanced: if/endif, for/next or endfor,
   while/endwhile, do/while, and startfunction/endfunction.
2. Every statement's first keyword is a known QuickBMS command, a
   label (``:name``), or a function-call-style name handled by the
   block rules above.
3. No line has an unterminated string literal.

This is a Western Heart clean implementation written for this repo;
it is not a copy of the private GRE linter of the same name.

Usage:
    python3 bms_lint.py script1.bms [script2.bms ...]
Exit 0 = all clean, 1 = problems found, 2 = usage error.
"""

import sys

# Block openers mapped to the tokens that may close them.
OPENERS = {
    "if": {"endif"},
    "for": {"next", "endfor"},
    "while": {"endwhile"},
    "do": {"while"},
    "startfunction": {"endfunction"},
}

# Middle tokens: they belong to an open block but do not close it.
MIDDLES = {"else", "elif", "elseif"}

# First-token keywords from the QuickBMS 0.12.0 command reference
# (aluigi.altervista.org/papers/quickbms.txt), plus the block tokens.
KNOWN = set(OPENERS) | MIDDLES | {
    "endif", "next", "endfor", "endwhile", "endfunction",
    "get", "getdstring", "getvarchr", "getct", "getarray", "getbits",
    "goto", "gotoct", "idstring", "idstringenc",
    "log", "clog", "logenc", "logarray", "append",
    "encryption", "comtype", "math", "xmath", "string", "set",
    "print", "break", "continue", "call", "calldll", "callfunction",
    "cleanexit", "exit", "findloc", "putarray", "sortarray",
    "stringarray", "padding", "filexor", "filerot", "filecrypt",
    "reimport", "slog", "slogenc", "open", "savepos",
    "strlen", "toupper", "tolower", "endian", "reverse",
    "include", "searcharray", "putbits", "putvarchr", "putdstring",
}


def strip_comments(raw_lines):
    """Remove # / // / /* */ comments, keeping line numbers."""
    lines = []
    in_block = False
    for lineno, raw in enumerate(raw_lines, 1):
        line = raw
        if in_block:
            if "*/" in line:
                line = line.split("*/", 1)[1]
                in_block = False
            else:
                lines.append((lineno, ""))
                continue
        while "/*" in line:
            before, _, after = line.partition("/*")
            if "*/" in after:
                line = before + after.split("*/", 1)[1]
            else:
                line = before
                in_block = True
                break
        if line.strip().startswith("#"):
            lines.append((lineno, ""))
            continue
        # Cut // comments outside string literals.
        out, in_string = [], False
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == '"':
                in_string = not in_string
                out.append(ch)
            elif ch == "/" and not in_string and line[i:i + 2] == "//":
                break
            else:
                out.append(ch)
            i += 1
        lines.append((lineno, "".join(out).strip()))
    return lines


def lint(path):
    errors = []
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = strip_comments(f.readlines())
    stack = []  # (block keyword, line number)
    for lineno, line in lines:
        if not line:
            continue
        if line.count('"') % 2 != 0:
            errors.append((lineno, "unterminated string literal"))
            continue
        tok = line.split(None, 1)[0].lower().rstrip(";")
        if tok.startswith(":"):
            continue  # label
        # A trailing `while COND` closes a `do` block.
        if tok == "while" and stack and stack[-1][0] == "do":
            stack.pop()
            continue
        if tok in OPENERS:
            stack.append((tok, lineno))
        elif tok in MIDDLES:
            if not stack or stack[-1][0] != "if":
                errors.append((lineno, "'%s' with no open 'if' block" % tok))
        elif tok in ("endif", "next", "endfor", "endwhile", "endfunction"):
            if not stack:
                errors.append((lineno, "stray '%s' with no open block" % tok))
                continue
            top, top_line = stack[-1]
            if tok in OPENERS[top]:
                stack.pop()
            else:
                errors.append((lineno, "'%s' does not close open '%s' "
                               "(line %d)" % (tok, top, top_line)))
        elif tok not in KNOWN:
            errors.append((lineno, "unknown command '%s'" % tok))
    for top, top_line in stack:
        errors.append((top_line, "unclosed '%s' block" % top))
    return errors


def main(paths):
    failed = False
    for path in paths:
        errs = lint(path)
        if errs:
            failed = True
            print("FAIL %s: %d problem(s)" % (path, len(errs)))
            for lineno, msg in errs[:20]:
                print("  line %d: %s" % (lineno, msg))
        else:
            print("OK   %s" % path)
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
