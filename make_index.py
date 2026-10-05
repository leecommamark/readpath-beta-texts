#!/usr/bin/env python3
"""Check the texts in this repo and write each bundle's index.json.

Run from the repo root:   python3 make_index.py

Every top-level folder named with a-z, 0-9 and hyphens (1-40 characters) is a
bundle; every *.txt directly inside it is a text. Everything is checked first;
if anything fails, the failures are all printed, nothing is written, and the
exit code is 1. Otherwise each bundle gets an index.json (the app reads it)
and the root gets an empty .nojekyll so GitHub Pages serves files as they are.

The repo shares an origin with the Read Path app (and so with testers' saved
progress), so any page or script file (.html .htm .js .mjs .svg .xml) is refused.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BUNDLE_NAME = re.compile(r"[a-z0-9-]{1,40}")
FORBIDDEN = (".html", ".htm", ".js", ".mjs", ".svg", ".xml")
MAX_UNITS = 20000   # the app's limit, in JavaScript .length units
TITLE_MAX = 60      # the app cuts titles here
# Exactly the app's CJK_RUN_SOURCE ranges.
CJK = re.compile("[㐀-䶿一-鿿\U00020000-\U0002ffff]")


def utf16_length(text):
    """Length as JavaScript's .length counts it (code points above U+FFFF count 2)."""
    return len(text.encode("utf-16-le")) // 2


def find_forbidden():
    found = []
    for folder, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            if name.lower().endswith(FORBIDDEN):
                found.append(os.path.relpath(os.path.join(folder, name), ROOT))
    return sorted(found)


def check_text(path, rel, failures, warnings):
    """Return (title, cjk_count, body) for a good text, or None."""
    with open(path, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        failures.append(f"{rel}: not valid UTF-8 (UTF-16 or another encoding?)")
        return None
    if "\x00" in text:
        failures.append(f"{rel}: contains NUL characters (UTF-16 saved as text?)")
        return None
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")
    # The app takes the first non-blank line as the title and the rest as
    # the text (as the starter text is read), so the checks are on the rest.
    first = next((i for i, l in enumerate(lines) if l.strip()), None)
    if first is None:
        failures.append(f"{rel}: empty file")
        return None
    title = lines[first].strip()
    if first:
        warnings.append(f"{rel}: line 1 is blank; line 1 should be the title")
    body = "\n".join(lines[first + 1:]).strip()
    count = len(CJK.findall(body))
    if count == 0:
        failures.append(f"{rel}: no Chinese characters after the title line")
        return None
    units = utf16_length(body)
    if units > MAX_UNITS:
        failures.append(f"{rel}: {units} characters, over the {MAX_UNITS} limit")
        return None
    if len(title) > TITLE_MAX:
        warnings.append(f"{rel}: title is {len(title)} characters; the app cuts it at {TITLE_MAX}")
    if len(lines) > first + 1 and lines[first + 1].strip():
        warnings.append(f"{rel}: the line after the title is not blank (title, blank line, then the text)")
    return title, count, body


def main():
    failures, warnings, bundles = [], [], []

    for rel in find_forbidden():
        failures.append(f"{rel}: pages and scripts are not allowed here "
                        "(this site shares an origin with Read Path and its testers' saved progress)")

    for folder in sorted(os.listdir(ROOT)):
        path = os.path.join(ROOT, folder)
        if not os.path.isdir(path) or not BUNDLE_NAME.fullmatch(folder):
            continue
        names = sorted(n for n in os.listdir(path)
                       if n.endswith(".txt") and os.path.isfile(os.path.join(path, n)))
        if not names:
            warnings.append(f"{folder}/: no .txt files, skipped")
            continue
        name, description = folder, ""
        meta = os.path.join(path, "bundle.md")
        if os.path.isfile(meta):
            try:
                with open(meta, encoding="utf-8-sig") as f:
                    meta_lines = f.read().replace("\r\n", "\n").split("\n")
                if meta_lines[0].strip():
                    name = meta_lines[0].strip()
                if len(meta_lines) > 1:
                    description = meta_lines[1].strip()
            except UnicodeDecodeError:
                failures.append(f"{folder}/bundle.md: not valid UTF-8")
        texts, seen = [], {}
        for n in names:
            rel = f"{folder}/{n}"
            result = check_text(os.path.join(path, n), rel, failures, warnings)
            if result is None:
                continue
            title, count, trimmed = result
            if trimmed in seen:
                warnings.append(f"{rel}: same text as {seen[trimmed]}")
            else:
                seen[trimmed] = rel
            texts.append({"file": n, "title": title, "chars": count})
        bundles.append((folder, {"format": 1, "name": name,
                                 "description": description, "texts": texts}))

    for w in warnings:
        print("warning:", w)
    if failures:
        for f in failures:
            print("error:", f, file=sys.stderr)
        print(f"{len(failures)} problem(s); nothing written.", file=sys.stderr)
        return 1

    for folder, index in bundles:
        with open(os.path.join(ROOT, folder, "index.json"), "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
            f.write("\n")
        n = len(index["texts"])
        print(f"{folder}: {n} text{'s' if n != 1 else ''}")
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
