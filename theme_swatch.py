#!/usr/bin/env python3
"""
theme_swatch.py - Render a visual grid of all <GlobalStyles> color entries
from a Notepad++ theme (stylers) XML file, as an HTML swatch sheet.

Usage:
    python theme_swatch.py <theme.xml> [output.html]

Each entry is drawn as a labeled frame containing two color boxes:
fgColor on the left, bgColor on the right. Either box is left blank
(hatched) if that attribute is absent from the XML. Entries are laid
out left-to-right in document order, wrapping to a new row.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from html import escape


def parse_global_styles(xml_path):
    """
    Parse the <GlobalStyles> section of a Notepad++ stylers XML file and
    return a list of dicts, one per <WidgetStyle> entry, in document
    order. Missing fgColor/bgColor attributes come back as None so the
    caller can render a blank/hatched box instead of guessing a color.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    global_styles = root.find(".//GlobalStyles")
    if global_styles is None:
        raise ValueError(f"No <GlobalStyles> section found in {xml_path}")

    entries = []
    for widget in global_styles.findall("WidgetStyle"):
        entries.append({
            "name": widget.get("name", "(unnamed)"),
            "style_id": widget.get("styleID", ""),
            "fg": widget.get("fgColor"),
            "bg": widget.get("bgColor"),
        })
    return entries


def color_box_html(hexval):
    """
    Return the HTML for one fg/bg color box. A missing color (hexval is
    None) renders as a hatched placeholder rather than a solid fill, so
    "not set in this theme" stays visually distinct from "set to black".
    """
    if hexval:
        return f'<div class="swatch" style="background:#{hexval};" title="#{hexval}"></div>'
    return '<div class="swatch swatch-empty" title="(not set)"></div>'


def build_html(entries, theme_name):
    """
    Assemble the full HTML page: a flex-wrap grid of entry frames, each
    showing name/styleID on top and the fg/bg boxes underneath, in the
    same left-to-right / wrap-to-next-row order as the input entries.
    """
    cells = []
    for e in entries:
        label = f'{escape(e["name"])}<br><span class="id">id {escape(e["style_id"])}</span>'
        cells.append(f'''
        <div class="entry">
          <div class="label">{label}</div>
          <div class="boxes">
            {color_box_html(e["fg"])}
            {color_box_html(e["bg"])}
          </div>
        </div>''')

    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>GlobalStyles swatches - {escape(theme_name)}</title>
<style>
  body {{ background:#222; color:#eee; font-family:sans-serif; padding:20px; }}
  h1 {{ font-size:16px; }}
  .grid {{ display:flex; flex-wrap:wrap; gap:6px; }}
  .entry {{ border:1px solid #555; width:120px; padding:4px; text-align:center; background:#2c2c2c; }}
  .label {{ font-size:11px; height:32px; overflow:hidden; }}
  .id {{ color:#999; }}
  .boxes {{ display:flex; height:36px; margin-top:4px; }}
  .swatch {{ flex:1; border:1px solid #000; }}
  .swatch-empty {{
    background-image: repeating-linear-gradient(45deg, #444, #444 4px, #333 4px, #333 8px);
  }}
</style>
</head>
<body>
<h1>GlobalStyles - {escape(theme_name)} ({len(entries)} entries)</h1>
<p>Left box = fgColor, right box = bgColor. Hatched = attribute not set.</p>
<div class="grid">
{''.join(cells)}
</div>
</body>
</html>'''


def main():
    # CLI entry point: parse args, run the parse/render pipeline, write output.
    if len(sys.argv) < 2:
        print("Usage: python theme_swatch.py <theme.xml> [output.html]")
        sys.exit(1)

    xml_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else xml_path.with_suffix(".swatches.html")

    entries = parse_global_styles(xml_path)
    html = build_html(entries, xml_path.stem)
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {out_path}")


if __name__ == "__main__":
    main()
