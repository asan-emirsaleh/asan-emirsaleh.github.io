#!/usr/bin/env python3
"""Build the Hugo Reveal page from the editable Obsidian slide manuscript."""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
from pathlib import Path


DEFAULT_SOURCE = (
    Path.home()
    / "Documents/PKM/obsidian/PROJECTS/author-lectures/launch/2026-09-25"
    / "Презентация — Нация не процент в ДНК-тесте.md"
)
SLIDE_SEPARATOR = re.compile(r"(?m)^[ \t]*___[ \t]*$")
COMMENT = re.compile(r"<!--.*?-->", re.S)
LAYOUT = re.compile(r"<!--\s*layout:\s*([a-z-]+)(?:;\s*kicker:\s*(.*?))?\s*-->", re.S)
IMAGE = re.compile(r"!\[[^\]]*\]\((attachments/[^)]+)\)")


def render_markdown(markdown: str) -> str:
    result = subprocess.run(
        ["pandoc", "-f", "markdown-implicit_figures", "-t", "html5", "--wrap=none"],
        input=markdown,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def copy_assets(source: Path, markdown: str, asset_dir: Path) -> None:
    asset_dir.mkdir(parents=True, exist_ok=True)
    for relative in sorted(set(IMAGE.findall(markdown))):
        image_path = source.parent / relative
        if not image_path.is_file():
            raise FileNotFoundError(f"В тексте указан отсутствующий файл: {image_path}")
        shutil.copy2(image_path, asset_dir / image_path.name)

    widget = source.parent / "attachments/genetic-drift.html"
    if not widget.is_file():
        raise FileNotFoundError(f"Не найден интерактивный виджет: {widget}")
    shutil.copy2(widget, asset_dir / widget.name)

    original = source.parent / "attachments/ancestry_types.png"
    cropped = asset_dir / "ancestry_types-cropped.png"
    if shutil.which("magick"):
        subprocess.run(["magick", str(original), "-trim", "+repage", str(cropped)], check=True)
    else:
        shutil.copy2(original, cropped)


def build(source: Path, repo: Path) -> None:
    manuscript = source.read_text(encoding="utf-8")
    blocks = [block.strip() for block in SLIDE_SEPARATOR.split(manuscript) if block.strip()]
    if not blocks:
        raise ValueError("В файле презентации нет слайдов")

    asset_dir = repo / "static/talks/crimea2040-01/assets"
    copy_assets(source, manuscript, asset_dir)

    slides: list[str] = []
    for index, block in enumerate(blocks, start=1):
        match = LAYOUT.search(block)
        if not match:
            raise ValueError(f"На слайде {index} нет комментария layout")
        layout = match.group(1)
        kicker = match.group(2).strip() if match.group(2) else ""
        body = COMMENT.sub("", block).strip()
        if layout == "widget":
            slides.append(
                '<section class="slide widget-slide" id="genetic-drift" '
                'data-background-iframe="./assets/genetic-drift.html" '
                "data-background-interactive data-preload></section>"
            )
            continue

        rendered = render_markdown(body)
        rendered = rendered.replace('src="attachments/', 'src="./assets/')
        rendered = rendered.replace(
            'src="./assets/ancestry_types.png"',
            'src="./assets/ancestry_types-cropped.png"',
        )
        label = f'<div class="eyebrow">{html.escape(kicker)}</div>' if kicker else ""
        link = '<a class="back-link" href="/talks/">← Все доклады</a>' if layout == "cover" else ""
        slides.append(
            f'<section class="slide layout-{layout}" data-slide="{index}">'
            f'<div class="frame">{label}<div class="body">{rendered}</div>{link}</div>'
            "</section>"
        )

    front_matter = """---
title: "Почему нация – не процент в ДНК-тесте"
date: 2026-10-01
draft: false
layout: reveal
description: "Презентация проекта Qırım 2040 о генетическом происхождении и ДНК-тестах."
summary: "Лекция о наследовании, популяционной генетике и интерпретации отчётов о происхождении."
tags: ["genetics", "genetic ancestry", "population genetics", "Qırım 2040"]
author: ["Asan Emirsaliev"]
---
"""
    target = repo / "content/talks/crimea2040-01/index.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        front_matter
        + "\n<!-- Сгенерировано из Obsidian; текст править в файле «Презентация — Нация не процент в ДНК-тесте.md». -->\n\n"
        + "\n\n".join(slides)
        + "\n",
        encoding="utf-8",
    )
    print(f"Обновлено {len(slides)} слайдов: {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Корень локального Hugo-репозитория",
    )
    args = parser.parse_args()
    if not args.source.is_file():
        parser.error(f"Не найден файл Obsidian: {args.source}")
    if not (args.repo / "hugo.yml").is_file():
        parser.error(f"Не найден Hugo-проект: {args.repo}")
    build(args.source, args.repo)


if __name__ == "__main__":
    main()
