#!/usr/bin/env python3
"""
theme_to_colors.py

Reads a Notepad++ theme XML file and a local select.json, and writes
colors.json in PrettyReMark's standard format.

select.json has the same shape as colors.json, except that any value may
either be:
  - a literal color string, e.g. "#1C2129"  -> copied through unchanged
  - a 2-element list, e.g. ["Tab color 1", "bgColor"] -> looked up in the
    theme file's <GlobalStyles> table, entry name="Tab color 1", using its
    fgColor or bgColor attribute

A line whose first non-whitespace character is ';' is treated as a comment
and ignored -- handy for disabling an entry while comparing alternatives.

Usage:
    python theme_to_colors.py themes\\Zenburn.xml
    python theme_to_colors.py themes\\Zenburn.xml my_test_select.json
"""

import re
import sys
import json
import argparse
import xml.etree.ElementTree as ET

DEFAULT_COLOR = "#C0C0C0"
SELECT_FILENAME = "select.json"
OUTPUT_FILENAME = "colors.json"
VALID_FIELDS = ("fgColor", "bgColor")
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

# A whole-line comment: ';' as the first non-whitespace character on the line. Lets you disable
# an entry in select.json (e.g. while comparing two values for the same key) without deleting it.
COMMENT_LINE_RE = re.compile(r"^[ \t]*;.*$", re.MULTILINE)

# Matches a comma followed by nothing but whitespace up to a closing '}' or ']'. Needed because
# commenting out the LAST entry in a section leaves the comma on the entry above it dangling,
# which is itself invalid JSON -- e.g. commenting out SidebarHoverBackgroundColor below would
# otherwise leave "...SidebarActiveBarColor": [...],\n}  with a trailing comma before the brace.
TRAILING_COMMA_RE = re.compile(r",(\s*[}\]])")


def strip_comments(text):
    """
    Strip select.json's ';'-prefixed whole-line comments, then clean up any trailing comma
    left dangling by a now-removed line, so the result is parseable by json.loads().
    """
    text = COMMENT_LINE_RE.sub("", text)
    text = TRAILING_COMMA_RE.sub(r"\1", text)
    return text


def parse_global_styles(theme_path):
    """
    Parse a Notepad++ theme XML file and return a dict mapping each
    <WidgetStyle name="..."> entry in <GlobalStyles> to its available
    fgColor/bgColor attributes (only the attributes actually present are
    included, since many entries only define one of the two).

    Raises SystemExit with a clear message if the file can't be parsed
    or has no <GlobalStyles> section -- both are fatal, since nothing
    downstream can proceed without this table.
    """
    try:
        tree = ET.parse(theme_path)
    except (ET.ParseError, OSError) as e:
        sys.exit(f"Error: couldn't read/parse theme file '{theme_path}': {e}")

    global_styles = tree.getroot().find(".//GlobalStyles")
    if global_styles is None:
        sys.exit(f"Error: no <GlobalStyles> section found in '{theme_path}'")

    styles = {}
    for widget in global_styles.findall("WidgetStyle"):
        name = widget.get("name")
        if name is None:
            continue
        entry = {}
        for field in VALID_FIELDS:
            value = widget.get(field)
            if value is not None:
                entry[field] = value
        styles[name] = entry
    return styles


def resolve_value(key, section, value, styles, errors):
    """
    Resolve a single select.json value to an output color string.

    - Plain strings pass through unchanged, but only if they actually look
      like a hex color ("#RRGGBB") -- anything else is almost certainly a
      lookup entry someone forgot to wrap in a [name, field] list, so it's
      reported as an error rather than silently written to colors.json.
    - 2-element [name, field] lists are looked up against `styles`; on any
      problem (malformed entry, unknown name, missing field on that entry)
      the problem is appended to `errors` and DEFAULT_COLOR is returned.
    """
    if isinstance(value, str):
        if HEX_COLOR_RE.match(value):
            return value, False
        errors.append(f"[{section}] {key}: {value!r} is not a valid "
                       f"\"#RRGGBB\" color and not a [\"Name\", \"field\"] "
                       f"lookup either")
        return DEFAULT_COLOR, True

    if not (isinstance(value, list) and len(value) == 2):
        errors.append(f"[{section}] {key}: malformed entry {value!r} "
                       f"(expected [\"Name\", \"fgColor\"|\"bgColor\"])")
        return DEFAULT_COLOR, True

    name, field = value
    if field not in VALID_FIELDS:
        errors.append(f"[{section}] {key}: field '{field}' must be "
                       f"'fgColor' or 'bgColor'")
        return DEFAULT_COLOR, True

    entry = styles.get(name)
    if entry is None:
        errors.append(f"[{section}] {key}: '{name}' not found in "
                       f"<GlobalStyles>")
        return DEFAULT_COLOR, True

    color = entry.get(field)
    if color is None:
        errors.append(f"[{section}] {key}: '{name}' has no {field} "
                       f"attribute")
        return DEFAULT_COLOR, True

    return f"#{color.upper()}", True


def build_colors(select_data, styles):
    """
    Walk select_data (as loaded from select.json) and produce the output
    dict for colors.json, along with a count of successful lookups and a
    list of error strings for anything that fell back to DEFAULT_COLOR.

    Top-level string values (like "_readme") pass through unchanged;
    top-level dict values (like "Light"/"Dark") are treated as sections
    and their entries are resolved individually.
    """
    output = {}
    replaced = 0
    errors = []

    for section, contents in select_data.items():
        if not isinstance(contents, dict):
            output[section] = contents
            continue

        resolved_section = {}
        for key, value in contents.items():
            resolved, was_lookup = resolve_value(key, section, value,
                                                   styles, errors)
            resolved_section[key] = resolved
            if was_lookup and resolved != DEFAULT_COLOR:
                replaced += 1
        output[section] = resolved_section

    return output, replaced, errors


def main():
    parser = argparse.ArgumentParser(
        description="Generate colors.json from an npp theme + select.json")
    parser.add_argument("theme_file", help="path to the npp theme XML file")
    parser.add_argument("select_file", nargs="?", default=SELECT_FILENAME,
                         help=f"path to the select file "
                              f"(default: {SELECT_FILENAME})")
    args = parser.parse_args()

    styles = parse_global_styles(args.theme_file)

    try:
        with open(args.select_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
        select_data = json.loads(strip_comments(raw_text))
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"Error: couldn't read/parse '{args.select_file}': {e}")

    output, replaced, errors = build_colors(select_data, styles)

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
        f.write("\n")

    print(f"Wrote {OUTPUT_FILENAME}: {replaced} color(s) resolved from "
          f"'{args.theme_file}'")
    if errors:
        print(f"{len(errors)} error(s) (fell back to {DEFAULT_COLOR}):")
        for err in errors:
            print(f"  - {err}")
    else:
        print("No errors.")


if __name__ == "__main__":
    main()
