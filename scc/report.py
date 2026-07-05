"""Render a Report to text, Markdown, or self-contained dark HTML."""

from __future__ import annotations

import html

from .audit import Report, KEEP, TUNE, COLLISION

STATUS_ORDER = {COLLISION: 0, TUNE: 1, KEEP: 2}


def _sorted_dispositions(report: Report):
    return sorted(report.dispositions, key=lambda d: (STATUS_ORDER.get(d.status, 3), d.skill))


def render_text(report: Report) -> str:
    lines: list[str] = []
    lines.append("Skill collision check")
    lines.append(f"roots: {', '.join(report.corpus.roots)}")
    lines.append(f"skills scanned: {report.skill_count}   threshold: {report.threshold:.2f}   near-dup ratio: {report.near_ratio:.2f}")
    if report.corpus.skipped:
        lines.append(f"skipped (no SKILL.md or unreadable): {len(report.corpus.skipped)}")
    lines.append("")

    counts = report.counts
    lines.append(f"Disposition: {counts[KEEP]} KEEP, {counts[TUNE]} TUNE, {counts[COLLISION]} COLLISION")
    lines.append("")
    for d in _sorted_dispositions(report):
        lines.append(f"  {d.status:<10} {d.skill:<28} {d.detail}")
    lines.append("")

    lines.append(f"Collision pairs ({len(report.collisions)})")
    if not report.collisions:
        lines.append("  none above threshold")
    for pair in report.collisions:
        lines.append(f"  [collision] {pair.a} <-> {pair.b}   jaccard-weighted score {pair.score:.2f}")
        if pair.shared_phrases:
            lines.append(f"      shared trigger phrases: " + ", ".join(f"'{p}'" for p in pair.shared_phrases))
        if pair.shared_keywords:
            lines.append(f"      shared keywords: " + ", ".join(pair.shared_keywords))
    lines.append("")

    lines.append(f"Shadowed skills ({len(report.shadows)})")
    if not report.shadows:
        lines.append("  none found")
    for s in report.shadows:
        lines.append(f"  [shadowed] {s.narrower} triggers are a strict subset of {s.broader}'s")
        lines.append(f"      suggestion: narrow {s.narrower}'s trigger; it is shadowed by {s.broader}")
    lines.append("")

    lines.append(f"Near-duplicate when-to-use wording ({len(report.near_dups)})")
    if not report.near_dups:
        lines.append("  none found")
    for d in report.near_dups:
        lines.append(f"  {d.a} <-> {d.b}   text-similarity ratio {d.ratio:.2f}")

    return "\n".join(lines)


def render_markdown(report: Report) -> str:
    md: list[str] = []
    md.append("# Skill collision check")
    md.append("")
    md.append(f"**Roots:** {', '.join(f'`{r}`' for r in report.corpus.roots)}  ")
    md.append(f"**Skills scanned:** {report.skill_count}  **Threshold:** {report.threshold:.2f}  **Near-dup ratio:** {report.near_ratio:.2f}")
    md.append("")
    counts = report.counts
    md.append(f"**Disposition:** {counts[KEEP]} KEEP, {counts[TUNE]} TUNE, {counts[COLLISION]} COLLISION")
    md.append("")
    md.append("| Status | Skill | Detail |")
    md.append("|---|---|---|")
    for d in _sorted_dispositions(report):
        md.append(f"| {d.status} | {d.skill} | {d.detail} |")
    md.append("")

    md.append(f"## Collision pairs ({len(report.collisions)})")
    md.append("")
    for pair in report.collisions:
        phrases = ", ".join(f"'{p}'" for p in pair.shared_phrases) or "-"
        keywords = ", ".join(pair.shared_keywords) or "-"
        md.append(f"- **{pair.a} <-> {pair.b}** (score {pair.score:.2f})  \n  shared trigger phrases: {phrases}  \n  shared keywords: {keywords}")
    if not report.collisions:
        md.append("None above threshold.")
    md.append("")

    md.append(f"## Shadowed skills ({len(report.shadows)})")
    md.append("")
    for s in report.shadows:
        md.append(f"- **{s.narrower}** is shadowed by **{s.broader}**  \n  suggestion: narrow {s.narrower}'s trigger; it is shadowed by {s.broader}")
    if not report.shadows:
        md.append("None found.")
    md.append("")

    md.append(f"## Near-duplicate when-to-use wording ({len(report.near_dups)})")
    md.append("")
    for d in report.near_dups:
        md.append(f"- **{d.a} <-> {d.b}** - text-similarity ratio {d.ratio:.2f}")
    if not report.near_dups:
        md.append("None found.")

    return "\n".join(md)


_STATUS_COLOR = {KEEP: "#22c55e", TUNE: "#f59e0b", COLLISION: "#ef4444"}


def render_html(report: Report) -> str:
    counts = report.counts

    rows = ""
    for d in _sorted_dispositions(report):
        color = _STATUS_COLOR.get(d.status, "#94a3b8")
        rows += (
            f"<tr><td><span class='status' style='background:{color}'>{d.status}</span></td>"
            f"<td><code>{html.escape(d.skill)}</code></td>"
            f"<td>{html.escape(d.detail)}</td></tr>"
        )

    collision_html = ""
    for pair in report.collisions:
        phrases = ", ".join(f"&lsquo;{html.escape(p)}&rsquo;" for p in pair.shared_phrases)
        keywords = ", ".join(html.escape(k) for k in pair.shared_keywords)
        collision_html += (
            f"<div class='card collision'><div class='pair'>{html.escape(pair.a)} &harr; {html.escape(pair.b)}"
            f"<span class='score'>score {pair.score:.2f}</span></div>"
            f"{f'<div class=\"row\">shared trigger phrases: {phrases}</div>' if phrases else ''}"
            f"{f'<div class=\"row\">shared keywords: {keywords}</div>' if keywords else ''}"
            f"</div>"
        )
    if not collision_html:
        collision_html = "<p class='sub'>None above threshold.</p>"

    shadow_html = ""
    for s in report.shadows:
        shadow_html += (
            f"<div class='card tune'><div class='pair'>{html.escape(s.narrower)} shadowed by {html.escape(s.broader)}</div>"
            f"<div class='row'>suggestion: narrow {html.escape(s.narrower)}'s trigger; it is shadowed by {html.escape(s.broader)}</div></div>"
        )
    if not shadow_html:
        shadow_html = "<p class='sub'>None found.</p>"

    near_html = ""
    for d in report.near_dups:
        near_html += (
            f"<div class='card tune'><div class='pair'>{html.escape(d.a)} &harr; {html.escape(d.b)}"
            f"<span class='score'>ratio {d.ratio:.2f}</span></div></div>"
        )
    if not near_html:
        near_html = "<p class='sub'>None found.</p>"

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skill collision check</title>
<style>
  body{{margin:0;background:#0f172a;color:#e2e8f0;font-family:-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.6;}}
  .wrap{{max-width:860px;margin:0 auto;padding:32px 20px 64px;}}
  h1{{font-size:1.6rem;margin:0 0 6px;}}
  h2{{font-size:1.15rem;border-bottom:1px solid #334155;padding-bottom:.3em;margin:1.8em 0 .6em;color:#fff;}}
  .sub{{color:#94a3b8;font-size:.9rem;}}
  .counts span{{display:inline-block;margin-right:16px;font-size:.9rem;color:#94a3b8;}}
  .counts b{{color:#fff;}}
  table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:.9rem;}}
  td{{padding:7px 10px;border-bottom:1px solid #334155;vertical-align:top;}}
  .status{{color:#0f172a;font-weight:700;border-radius:10px;padding:1px 9px;font-size:.72rem;text-transform:uppercase;white-space:nowrap;}}
  .card{{background:#1e293b;border:1px solid #334155;border-radius:8px;padding:10px 14px;margin:8px 0;font-size:.9rem;}}
  .card.collision{{border-left:3px solid #ef4444;}}
  .card.tune{{border-left:3px solid #f59e0b;}}
  .pair{{font-weight:600;color:#fff;}}
  .score{{float:right;color:#94a3b8;font-weight:400;font-size:.82rem;}}
  .row{{color:#cbd5e1;font-size:.85rem;margin-top:4px;}}
  code{{background:#243349;padding:1px 6px;border-radius:5px;font-size:.85em;color:#cbd5e1;}}
</style></head><body><div class="wrap">
<h1>Skill collision check</h1>
<p class="sub">roots: {html.escape(', '.join(report.corpus.roots))}</p>
<div class="counts">
  <span>Skills: <b>{report.skill_count}</b></span>
  <span>KEEP: <b>{counts[KEEP]}</b></span>
  <span>TUNE: <b>{counts[TUNE]}</b></span>
  <span>COLLISION: <b>{counts[COLLISION]}</b></span>
</div>
<h2>Disposition</h2>
<table>{rows}</table>
<h2>Collision pairs ({len(report.collisions)})</h2>
{collision_html}
<h2>Shadowed skills ({len(report.shadows)})</h2>
{shadow_html}
<h2>Near-duplicate when-to-use wording ({len(report.near_dups)})</h2>
{near_html}
<p class="sub" style="margin-top:28px">Generated by skill-collision-checker. Suggest-only: no SKILL.md file was edited.</p>
</div></body></html>"""
