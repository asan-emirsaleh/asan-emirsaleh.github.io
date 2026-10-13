#!/usr/bin/env python3
"""Read the editable PKM presentation note and update the Hugo slide page."""
from pathlib import Path
import argparse
import html
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = Path.home() / 'Documents/PKM/obsidian/PROJECTS/author-lectures/PKM-01/Презентация — От информации к знанию.md'
ALT = {
    'obsidian_dirs.png': 'Структура папок авторского хранилища Obsidian',
    'obsidian_graph.png': 'Граф связей заметок в авторском хранилище Obsidian',
    'zotero_dirs.png': 'Коллекции авторской библиотеки Zotero',
}

def markdown(text):
    return subprocess.run(['pandoc', '--from=gfm', '--to=html5'], input=text, text=True, capture_output=True, check=True).stdout.strip()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    source = args.source.resolve()
    raw = source.read_text()
    assets = ROOT / 'static/talks/pkm-01/assets'
    assets.mkdir(parents=True, exist_ok=True)
    sections = []
    for block in re.split(r'\n---\n', raw.strip()):
        layout_match = re.search(r'<!--\s*slide:\s*\d+;\s*layout:\s*([a-z-]+)\s*-->', block)
        layout = layout_match.group(1) if layout_match else 'text'
        text = re.sub(r'<!--[\s\S]*?-->', '', block).strip()
        if not text:
            continue
        lines = text.splitlines()
        title = re.sub(r'^#\s+', '', lines.pop(0))
        body = '\n'.join(lines).strip()
        image = re.search(r'!\[\[([^|\]]+)(?:\|\d+)?\]\]', body)
        if image:
            reference = Path(image.group(1))
            candidates = [source.parent / reference, source.parent / 'files' / reference.name]
            for ancestor in source.parents:
                if (ancestor / '.obsidian').is_dir():
                    candidates.insert(0, ancestor / reference)
                    break
            image_path = next((p for p in candidates if p.is_file()), None)
            if image_path is None:
                raise FileNotFoundError(reference)
            shutil.copy2(image_path, assets / reference.name)
            body = body.replace(image.group(0), '').strip()
            body_html = '<figure><img src="./assets/{}" alt="{}" tabindex="0"></figure><div class="image-text">{}</div>'.format(html.escape(reference.name, quote=True), html.escape(ALT.get(reference.name, title), quote=True), markdown(body))
        else:
            body_html = markdown(body)
        number = len(sections) + 1
        sections.append('<section class="slide layout-{}" id="slide-{}" data-slide="{}"><div class="frame"><h1>{}</h1><div class="body">{}</div></div></section>'.format(layout, number, number, html.escape(title), body_html))
    target = ROOT / 'content/talks/pkm-01/index.md'
    current = target.read_text()
    if not current.startswith('---\n'):
        raise ValueError('Missing Hugo front matter')
    front = current.split('---', 2)[1]
    target.write_text('---' + front + '---\n\n' + '\n\n'.join(sections) + '\n')
    print(f'Updated {target.relative_to(ROOT)}: {len(sections)} slides')

if __name__ == '__main__':
    main()
