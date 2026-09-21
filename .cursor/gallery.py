#!/usr/bin/env python3
"""Generate a static preview gallery for the sketch-icons asset library.

Scans the repository for SVG and PNG icon assets and writes a single
self-contained HTML page to .preview/index.html. The page references the
assets with absolute web paths so it can be served from the repository root
(e.g. `python3 -m http.server 8080`).
"""
from __future__ import annotations

import html
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / ".preview"
OUTPUT_FILE = OUTPUT_DIR / "index.html"

# Only surface web-renderable raster/vector formats in the gallery grid.
EXTENSIONS = {".svg", ".png"}
# Directories that are not part of the browsable asset sets.
SKIP_DIRS = {".git", ".cursor", ".preview"}


def collect_sets() -> list[tuple[str, list[Path]]]:
    """Return (section_title, sorted asset paths) grouped by containing dir."""
    groups: dict[Path, list[Path]] = {}
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel_dir = Path(dirpath).relative_to(REPO_ROOT)
        for name in filenames:
            if Path(name).suffix.lower() in EXTENSIONS:
                groups.setdefault(rel_dir, []).append(Path(dirpath) / name)

    sections: list[tuple[str, list[Path]]] = []
    for rel_dir in sorted(groups, key=lambda p: str(p).lower()):
        assets = sorted(groups[rel_dir], key=lambda p: p.name.lower())
        title = str(rel_dir) if str(rel_dir) != "." else "root"
        sections.append((title, assets))
    return sections


def render(sections: list[tuple[str, list[Path]]]) -> str:
    total = sum(len(a) for _, a in sections)
    parts: list[str] = []
    parts.append(
        """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>sketch-icons preview</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: #0f1115;
    color: #e6e8eb;
  }
  header {
    padding: 28px 32px 20px;
    border-bottom: 1px solid #232833;
    position: sticky;
    top: 0;
    background: rgba(15,17,21,0.92);
    backdrop-filter: blur(8px);
    z-index: 10;
  }
  header h1 { margin: 0 0 6px; font-size: 22px; letter-spacing: .2px; }
  header p { margin: 0; color: #9aa4b2; font-size: 14px; }
  main { padding: 8px 32px 64px; }
  section h2 {
    font-size: 15px;
    font-weight: 600;
    color: #c7d0dc;
    margin: 32px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1c212b;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 14px;
  }
  .card {
    background: #171b22;
    border: 1px solid #232833;
    border-radius: 12px;
    padding: 14px 10px 10px;
    text-align: center;
    transition: transform .12s ease, border-color .12s ease;
  }
  .card:hover { transform: translateY(-2px); border-color: #3a4150; }
  .thumb {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #ffffff;
    border-radius: 8px;
    margin-bottom: 8px;
  }
  .thumb img { max-width: 52px; max-height: 52px; }
  .name {
    font-size: 11px;
    color: #9aa4b2;
    word-break: break-word;
    line-height: 1.3;
  }
  .badge {
    display: inline-block;
    font-size: 10px;
    color: #7f8a99;
    border: 1px solid #2a303b;
    border-radius: 6px;
    padding: 1px 6px;
    margin-left: 6px;
  }
</style>
</head>
<body>
<header>
  <h1>sketch-icons preview</h1>
  <p>__TOTAL__ assets across __SECTIONS__ folders &middot; served live from the repository</p>
</header>
<main>
""".replace("__TOTAL__", str(total)).replace("__SECTIONS__", str(len(sections)))
    )

    for title, assets in sections:
        parts.append(f'<section>\n<h2>{html.escape(title)} <span class="badge">{len(assets)}</span></h2>\n<div class="grid">\n')
        for asset in assets:
            rel = asset.relative_to(REPO_ROOT).as_posix()
            web = "/" + "/".join(html.escape(seg) for seg in rel.split("/"))
            label = html.escape(asset.stem)
            ext = html.escape(asset.suffix.lstrip(".").upper())
            parts.append(
                f'  <div class="card">'
                f'<div class="thumb"><img loading="lazy" src="{web}" alt="{label}"></div>'
                f'<div class="name">{label}<span class="badge">{ext}</span></div>'
                f"</div>\n"
            )
        parts.append("</div>\n</section>\n")

    parts.append("</main>\n</body>\n</html>\n")
    return "".join(parts)


def main() -> None:
    sections = collect_sets()
    OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(render(sections), encoding="utf-8")
    total = sum(len(a) for _, a in sections)
    print(f"Wrote {OUTPUT_FILE.relative_to(REPO_ROOT)} ({total} assets, {len(sections)} sections)")


if __name__ == "__main__":
    main()
