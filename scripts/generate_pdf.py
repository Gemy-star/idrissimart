#!/usr/bin/env python3
"""
Generate a styled PDF from SYSTEM_FLOWS_ARABIC.md
Uses brand colors and design system from static/css/style.css
"""

import os
import sys

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

MD_FILE = os.path.join(BASE_DIR, "docs", "SYSTEM_FLOWS_ARABIC.md")
OUT_FILE = os.path.join(BASE_DIR, "docs", "SYSTEM_FLOWS_ARABIC.pdf")

# ── Read Markdown ────────────────────────────────────────────────────────────
with open(MD_FILE, encoding="utf-8") as f:
    md_text = f.read()

md_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "toc", "nl2br"],
)

# ── PDF-specific CSS (brand colors extracted from style.css) ─────────────────
PDF_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

/* ── Page Setup ── */
@page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
    direction: rtl;

    @top-center {
        content: "إدريسي مارت — دليل منطق الأعمال";
        font-family: 'Cairo', sans-serif;
        font-size: 9pt;
        color: #6b4c7a;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 4pt;
    }

    @bottom-right {
        content: counter(page) " / " counter(pages);
        font-family: 'Cairo', sans-serif;
        font-size: 8pt;
        color: #888888;
    }

    @bottom-left {
        content: "IdrissiMart — Business Logic Flows";
        font-family: 'Cairo', sans-serif;
        font-size: 8pt;
        color: #888888;
    }
}

/* ── CSS Variables (from style.css) ── */
:root {
    --primary-color:    #4b315e;
    --primary-dark:     #3a2449;
    --secondary-color:  #ff6001;
    --accent-purple:    #6b4c7a;
    --accent-orange:    #ff8534;
    --bg-primary:       #f5f7fa;
    --bg-secondary:     #f5f5f5;
    --text-primary:     #000000;
    --text-secondary:   #333333;
    --text-muted:       #666666;
    --border-color:     #e0e0e0;
    --white-color:      #ffffff;
}

/* ── Base ── */
* {
    box-sizing: border-box;
    font-family: 'Cairo', 'Arial', sans-serif;
}

html, body {
    direction: rtl;
    text-align: right;
    background: #ffffff;
    color: var(--text-secondary);
    font-size: 10.5pt;
    line-height: 1.75;
}

/* ── Cover / Main Title ── */
h1:first-of-type {
    background: linear-gradient(135deg, var(--primary-color), var(--accent-purple));
    color: var(--white-color);
    text-align: center;
    padding: 22pt 16pt;
    border-radius: 10pt;
    font-size: 20pt;
    font-weight: 800;
    margin-bottom: 6pt;
    page-break-before: avoid;
}

/* ── Headings ── */
h1 {
    color: var(--primary-color);
    font-size: 17pt;
    font-weight: 800;
    margin-top: 18pt;
    margin-bottom: 8pt;
    padding-bottom: 5pt;
    border-bottom: 3px solid var(--secondary-color);
}

h2 {
    color: var(--primary-dark);
    font-size: 13.5pt;
    font-weight: 700;
    margin-top: 16pt;
    margin-bottom: 6pt;
    padding: 6pt 10pt;
    background: linear-gradient(90deg, rgba(75,49,94,0.08), transparent);
    border-right: 4px solid var(--primary-color);
    border-radius: 0 6pt 6pt 0;
    page-break-after: avoid;
}

h3 {
    color: var(--accent-purple);
    font-size: 11.5pt;
    font-weight: 700;
    margin-top: 12pt;
    margin-bottom: 5pt;
    page-break-after: avoid;
}

h4 {
    color: var(--secondary-color);
    font-size: 10.5pt;
    font-weight: 700;
    margin-top: 10pt;
    margin-bottom: 4pt;
}

/* ── Paragraphs ── */
p {
    margin-bottom: 8pt;
    text-align: justify;
}

/* ── Blockquotes ── */
blockquote {
    background: rgba(75, 49, 94, 0.06);
    border-right: 4px solid var(--primary-color);
    padding: 8pt 12pt;
    margin: 10pt 0;
    border-radius: 0 6pt 6pt 0;
    color: var(--text-muted);
    font-size: 10pt;
}

blockquote p { margin: 0; }

/* ── Code blocks (flow diagrams) ── */
pre {
    background: var(--primary-dark);
    color: #e8d5f5;
    padding: 12pt;
    border-radius: 8pt;
    font-size: 8.5pt;
    line-height: 1.6;
    overflow: hidden;
    white-space: pre-wrap;
    word-break: break-word;
    direction: ltr;
    text-align: left;
    margin: 10pt 0;
    border-left: 4px solid var(--secondary-color);
    page-break-inside: avoid;
}

code {
    background: rgba(75, 49, 94, 0.08);
    color: var(--primary-dark);
    padding: 1pt 4pt;
    border-radius: 3pt;
    font-size: 9pt;
    font-family: 'Courier New', monospace;
}

pre code {
    background: transparent;
    color: inherit;
    padding: 0;
    font-size: 8.5pt;
}

/* ── Tables ── */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

thead {
    background: linear-gradient(135deg, var(--primary-color), var(--accent-purple));
    color: var(--white-color);
}

thead th {
    padding: 8pt 10pt;
    text-align: right;
    font-weight: 700;
    font-size: 10pt;
    border: none;
}

tbody tr:nth-child(even) {
    background: rgba(75, 49, 94, 0.04);
}

tbody tr:nth-child(odd) {
    background: #ffffff;
}

tbody tr:hover {
    background: rgba(255, 96, 1, 0.06);
}

td {
    padding: 7pt 10pt;
    text-align: right;
    border-bottom: 1px solid var(--border-color);
    vertical-align: middle;
}

/* ── Lists ── */
ul, ol {
    padding-right: 18pt;
    padding-left: 0;
    margin-bottom: 8pt;
}

li {
    margin-bottom: 4pt;
    text-align: right;
}

ul li::marker {
    color: var(--secondary-color);
    font-weight: bold;
}

ol li::marker {
    color: var(--primary-color);
    font-weight: bold;
}

/* ── Horizontal rules ── */
hr {
    border: none;
    border-top: 2px solid var(--border-color);
    margin: 16pt 0;
}

/* ── Strong / Em ── */
strong {
    color: var(--primary-dark);
    font-weight: 700;
}

em {
    color: var(--accent-purple);
}

/* ── Table of Contents ── */
.toc {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8pt;
    padding: 12pt 16pt;
    margin: 12pt 0;
}

/* ── Page breaks ── */
h1, h2 {
    page-break-before: auto;
}

h2 + * {
    page-break-before: avoid;
}

/* Prevent orphaned headings */
h1, h2, h3 {
    page-break-after: avoid;
}

/* Section spacing */
h2 {
    margin-top: 20pt;
}
"""

# ── Build full HTML document ─────────────────────────────────────────────────
HTML_DOC = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دليل منطق الأعمال — إدريسي مارت</title>
</head>
<body>
{md_body}
</body>
</html>"""

# ── Generate PDF ─────────────────────────────────────────────────────────────
print(f"[+] Converting markdown → HTML …")
print(f"[+] Applying brand styles from style.css …")
print(f"[+] Generating PDF → {OUT_FILE}")

font_config = FontConfiguration()
css = CSS(string=PDF_CSS, font_config=font_config)
html = HTML(string=HTML_DOC, base_url=BASE_DIR)
html.write_pdf(OUT_FILE, stylesheets=[css], font_config=font_config)

size_kb = os.path.getsize(OUT_FILE) // 1024
print(f"[✓] PDF created: {OUT_FILE}  ({size_kb} KB)")
