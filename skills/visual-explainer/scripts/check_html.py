#!/usr/bin/env python3
"""Check the shared HTML structure, design tokens, section order, and obvious
external runtime dependencies.

The design-token check keeps the shared dark/cyan style from drifting: the
template's stylesheet (templates/explainer.html) defines these tokens as CSS
custom properties, and a document copied from the template carries them all.
A missing token means the stylesheet was rewritten instead of reused. The
expected values come from references/design-system.md — update EXPECTED_TOKENS
in the same change as that table and assets/mermaid-config.json.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

# (token name, hex value) from references/design-system.md. Checked
# case-insensitively against <style> blocks only — inline style attributes
# do not count, so a single coloured element cannot fake the stylesheet.
EXPECTED_TOKENS = [
    ("background", "#101418"),
    ("surface", "#171D23"),
    ("raised", "#202830"),
    ("border", "#36434F"),
    ("text", "#E8EDF2"),
    ("muted", "#A8B5C2"),
    ("accent", "#67D4E8"),
    ("accent-soft", "#182D34"),
]

REQUIRED_SECTIONS = ("overview", "details", "next-steps")


class DocumentCheck(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.id_order = []
        self.local_links = []
        self.errors = []
        self.svg_count = 0
        self.script_depth = 0
        self.style_depth = 0
        self.scripts = []
        self.styles = []
        self.style_blocks = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        identity = values.get('id')
        if identity:
            if identity in self.ids:
                self.errors.append(f'Duplicate id: {identity}')
            else:
                self.id_order.append(identity)
            self.ids.add(identity)
        if tag in {'iframe', 'form', 'object', 'embed', 'base'}:
            self.errors.append(f'Unsupported element: {tag}')
        if tag == 'script':
            self.script_depth += 1
            if 'src' in values:
                self.errors.append('External script dependency')
        if tag == 'style':
            self.style_depth += 1
        if tag == 'link' and values.get('rel', '').lower() in {'stylesheet', 'preload', 'modulepreload'}:
            self.errors.append('External stylesheet/preload dependency')
        for key in ('src', 'srcset', 'poster'):
            if values.get(key) and not values[key].startswith('data:'):
                self.errors.append(f'Non-inline {tag} {key}: {values[key]}')
        if tag in {'image', 'use'}:
            for key in ('href', 'xlink:href'):
                value = values.get(key, '')
                if value and not value.startswith(('#', 'data:')):
                    self.errors.append('External SVG resource')
        if tag == 'a' and values.get('href', '').startswith('#'):
            self.local_links.append(values['href'][1:])
        if tag == 'svg':
            self.svg_count += 1
            if not values.get('viewbox') or not values.get('aria-labelledby'):
                self.errors.append('SVG needs viewBox and aria-labelledby')
            self.local_links.extend(values.get('aria-labelledby', '').split())
        if tag == 'pre' and 'mermaid' in values.get('class', '').split():
            self.errors.append('Unrendered Mermaid container; inline a rendered SVG')
        if values.get('style'):
            self.styles.append(values['style'])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.script_depth = max(0, self.script_depth - 1)
        if tag == 'style':
            self.style_depth = max(0, self.style_depth - 1)

    def handle_data(self, data):
        if self.script_depth:
            self.scripts.append(data)
        if self.style_depth:
            self.styles.append(data)
            self.style_blocks.append(data)


def check(path):
    parser = DocumentCheck()
    parser.feed(Path(path).read_text(encoding='utf-8-sig'))
    for identity in REQUIRED_SECTIONS:
        if identity not in parser.ids:
            parser.errors.append(f'Missing document section: {identity}')
    if all(identity in parser.ids for identity in REQUIRED_SECTIONS):
        positions = [parser.id_order.index(identity) for identity in REQUIRED_SECTIONS]
        if positions != sorted(positions):
            parser.errors.append(
                'Document sections out of order: expected overview, then details, then next-steps')
    css = '\n'.join(parser.style_blocks).lower()
    for name, value in EXPECTED_TOKENS:
        if value.lower() not in css:
            parser.errors.append(
                f'Missing design token: {name} {value} (see references/design-system.md)')
    for identity in parser.local_links:
        if identity and identity not in parser.ids:
            parser.errors.append(f'Broken in-page reference: {identity}')
    css = '\n'.join(parser.styles)
    urls = re.findall(r'url\(([^)]*)\)', css, re.I)
    if re.search(r'@import\b', css, re.I) or any(not value.strip().strip('\"\'').startswith(('#', 'data:')) for value in urls):
        parser.errors.append('Possible external CSS dependency')
    js = '\n'.join(parser.scripts)
    if re.search(r'\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\b|\bimport\s*(?:\(|[\"\'{*])', js):
        parser.errors.append('Possible runtime network dependency')
    if parser.errors:
        for error in parser.errors:
            print(f'ERROR: {error}')
        return 1
    print(f'HTML structure passed; {parser.svg_count} inline SVG(s). Visually inspect the final document.')
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python check_html.py <document.html>')
    raise SystemExit(check(sys.argv[1]))
