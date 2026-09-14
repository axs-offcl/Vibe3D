#!/usr/bin/env python3
"""Vibe3D status dashboard generator.

Usage:
    python scripts/gen-dashboard.py            # writes .freebuff/dashboard.html

Renders a static HTML overview from docs/CI_REPAIR_PLAN.md, PROJECT_PLAN.md
and docs/STRIP_LIST.md. Re-run after editing those docs to refresh the page.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / ".freebuff" / "dashboard.html"


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    return s


def md_table(md: str) -> str:
    rows = [r for r in md.splitlines() if r.strip().startswith("|")]
    if not rows:
        return ""
    out = ["<table>"]
    for i, r in enumerate(rows):
        if set(r.replace("|", "").strip()) <= {"-", ":", " "}:
            continue
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        tag = "th" if i == 0 else "td"
        out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


def list_md(md: str, ordered: bool) -> str:
    """Markdown list -> HTML, joining indented continuation lines into items."""
    item = re.compile(r"^\s*(?:\d+\.|[-*])\s+(.*)$")
    cont = re.compile(r"^\s{2,}(\S.*)$")
    items, cur = [], None
    for line in md.splitlines():
        m = item.match(line)
        if m:
            cur = [m.group(1)]
            items.append(cur)
        elif cur is not None and line.strip() and (c := cont.match(line)):
            cur.append(c.group(1))
    tag = "ol" if ordered else "ul"
    return f"<{tag}>" + "".join(f"<li>{inline(' '.join(i))}</li>" for i in items) + f"</{tag}>"


def section(title: str, body: str) -> str:
    return f"<section><h2>{html.escape(title)}</h2>{body}</section>"


plan = read("docs/CI_REPAIR_PLAN.md")
strip = read("docs/STRIP_LIST.md")
proj = read("PROJECT_PLAN.md")


def between(md: str, start: str, end: str) -> str:
    try:
        rest = md.split(start, 1)[1]
    except IndexError:
        return ""
    return rest.split(end, 1)[0] if end else rest


verified = between(plan, "## Verified working (no change needed)", "## Confirmed workflow bugs")
bugs = between(plan, "## Confirmed workflow bugs", "## Fix steps")
steps = between(plan, "## Fix steps", "## Risks / caveats")
risks = between(plan, "## Risks / caveats", "")
phase1 = between(strip, "## Phase 1", "## Phase 2")
phase2 = between(strip, "## Phase 2", "## Keep")
keeps = between(strip, "## Keep", "Log every removal")
constraints = between(proj, "## Build constraints", "## Next steps")

phases = [
    ("1", "CI green", "done", "done", "runs #27-#29 green; rolling libs cache, era-gap patches"),
    ("2", "CMake-level strip", "done", "done", "10 WITH_* flags + NDOF/i18n/OpenSubdiv lightness flags"),
    ("3", "Source-level strip (waves)", "active", "Wave 1 green (run #31)", "animation editors stripped: 3 libs + 6 out-of-lib call sites; Vibe3D.exe builds + uploads"),
    ("4", "Scripting platform UI", "todo", "planned", "floating side panel: add, run, manage script packs (KAM-style)"),
    ("5", "Script packs & ecosystem", "todo", "planned", "pack format + docs; GTA SA pack as the first example"),
]

phase_html = "".join(
    f'<div class="phase {cls}"><span class="num">{n}</span><div><b>{html.escape(t)}</b>'
    f'<span class="badge">{html.escape(st)}</span><p>{html.escape(d)}</p></div></div>'
    for n, t, cls, st, d in phases
)

CSS = """
:root{--bg:#14161a;--fg:#d7dae0;--mut:#8b93a1;--acc:#4772b3;--ok:#4caf50;--warn:#e2b93b;--card:#1c1f26}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,'Segoe UI',Roboto,sans-serif}
header{padding:28px 32px 20px;border-bottom:1px solid #2a2e36;background:linear-gradient(180deg,#1a1e26,var(--bg))}
h1{margin:0;font-size:24px;letter-spacing:.5px}
h1 span{color:var(--acc)}
header p{margin:6px 0 0;color:var(--mut)}
main{max-width:980px;margin:0 auto;padding:24px 32px 64px}
section{margin:28px 0}
h2{font-size:13px;text-transform:uppercase;letter-spacing:1.5px;color:var(--mut);border-bottom:1px solid #2a2e36;padding-bottom:8px}
table{width:100%;border-collapse:collapse;font-size:13.5px}
td,th{padding:7px 10px;border-bottom:1px solid #262b33;text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:600}
code{background:#262b33;padding:1px 6px;border-radius:4px;font-size:12.5px;color:#9cc0f5}
ul,ol{margin:8px 0;padding-left:22px}
li{margin:5px 0}
.phase{display:flex;gap:14px;padding:12px 14px;border:1px solid #262b33;border-radius:8px;margin:8px 0;background:var(--card);align-items:flex-start}
.phase .num{width:28px;height:28px;border-radius:50%;background:var(--acc);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0}
.phase .badge{font-size:10.5px;text-transform:uppercase;letter-spacing:1px;padding:2px 8px;border-radius:10px;margin-left:10px;vertical-align:middle}
.phase.active{border-color:var(--acc)}
.phase.done .badge{background:#2f5233;color:#8fd694}
.phase.done-partial .badge{background:#3d5c3e;color:#8fd694}
.phase.active .badge{background:#3a4d6b;color:#9cc0f5}
.phase.todo .badge{background:#333842;color:var(--mut)}
.phase p{margin:4px 0 0;color:var(--mut);font-size:13.5px}
footer{color:var(--mut);font-size:12px;border-top:1px solid #2a2e36;margin-top:40px;padding-top:16px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media(max-width:760px){.grid{grid-template-columns:1fr}}
"""

ci_body = (
    '<p style="color:var(--ok)"><b>GREEN — run #27 built Vibe3D.exe and '
    'uploaded the Vibe3D-windows-x64 artifact.</b></p>'
    '<p>The fix stack, peeled in order: IP-lottery resumable fetch + rolling '
    'cache → era-correct libs <b>r62438</b> (OCIO v1 + python/37) → '
    'audaspace <code>&lt;string&gt;</code> → <code>/wd5287</code> → OIIO '
    'fmt <code>_SECURE_SCL</code> guard → OIIO link shims via '
    '<code>/ALTERNATENAME</code>. Full trail: '
    '<code>docs/CI_REPAIR_PLAN.md</code>.</p>'
    + list_md(steps, True)
)

page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vibe3D — Project Dashboard</title><style>{CSS}</style></head>
<body>
<header>
<h1><span>◆</span> Vibe3D</h1>
<p>Lightweight, highly scriptable Blender fork — a fast scripting host bridging 3ds Max and Blender</p>
</header>
<main>
{section("Roadmap", phase_html)}
{section("Risks / caveats", list_md(risks, False)) if risks.strip() else ''}
{section("CI status — windows-latest build", ci_body)}
<div class="grid">
{section("Verified working", md_table(verified))}
{section("Confirmed workflow bugs", list_md(bugs, True))}
</div>
{section("Strip list — Phase 1 (CMake flags + lightness flags, in CI)", md_table(phase1))}
<div class="grid">
{section("Strip list — Phase 2 Wave 1 (animation editors, in CI)", md_table(phase2))}
{section("Keep (core of the scripting host)", f'<p>{inline(keeps.strip())}</p>')}
</div>
{section("Build constraints (local, measured 2026-09-12)", list_md(constraints, False))}
<footer>Generated by <code>scripts/gen-dashboard.py</code> from docs/CI_REPAIR_PLAN.md, docs/STRIP_LIST.md, PROJECT_PLAN.md — re-run the script to refresh after doc edits. Data probed live 2026-09-13.</footer>
</main></body></html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(page, encoding="utf-8")
print(f"dashboard written: {OUT} ({len(page):,} bytes)")
