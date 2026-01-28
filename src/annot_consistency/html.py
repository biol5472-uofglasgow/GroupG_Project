from annot_consistency.models import ChangeRecord
import json
import os
from datetime import datetime, timezone
import matplotlib.pyplot as plt

def plot_counts(outdir: str, counts: dict[str, dict[str, int]], prefix: str) -> str:
    '''
    Creates a bar plot of the counts of the different changes types per entity type,
    saved as a png file to be used in the html report
    '''
    entity_types = sorted(counts.keys())
    added = [counts[et].get('added', 0) for et in entity_types]
    removed = [counts[et].get('removed', 0) for et in entity_types]
    changed = [counts[et].get('changed', 0) for et in entity_types]

    x = list(range(len(entity_types)))

    plt.figure()
    plt.bar(x, added, label = 'Added')
    plt.bar(x, removed, bottom=added, label="removed")
    bottoms = [a + r for a, r in zip(added, removed)]
    plt.bar(x, changed, bottom=bottoms, label="changed")
    plt.xticks(x, entity_types, rotation=45, ha="right")
    plt.ylabel("Count")
    plt.title("Change counts by entity type")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(outdir, f'{prefix}_report.png')
    plt.savefig(plot_path, dpi=150)
    plt.close()

    return plot_path

def write_htmlreport(outdir: str, changes: list[ChangeRecord], summary_result: tuple[str, dict[str, dict[str, int]]],
                     run_json_path: str, title: str = 'Two release annotation consistency report') -> str:
    '''
    Generate report.html and report.png. Takes in outdir: output directory, changes: ChangeRecord list from diff stage 
    (taken from counts in io, used in cli), summary_result: (summary_path, counts) returned by io.write_summary_tsv(),
    run_json_path: path returned by io.write_run_json() and a title: HTML title.
    '''
    summary_path, counts = summary_result
    plot_counts(outdir, counts)

    entity_types = sorted(counts.keys())
    total_added = sum(counts[et].get('added', 0) for et in entity_types)
    total_removed = sum(counts[et].get('removed', 0) for et in entity_types)
    total_changed = sum(counts[et].get('changed', 0) for et in entity_types)
    total_all = total_added + total_removed + total_changed

    with open(run_json_path, 'r', encoding='utf-8') as file:
        run_meta = json.load(file)

    tool = run_meta['tool']
    inputs = run_meta['inputs']

    tool_name = tool['name']
    tool_version = tool['version']
    timestamp_utc = run_meta['timestamp_utc']
    release_a = inputs['release_a']
    release_b = inputs['release_b']

    html: list[str] = []
    html.append("<!doctype html>")
    html.append("<html><head><meta charset='utf-8'>")
    html.append(f'<title>{title}</title>')
    html.append("<style>"
        "body{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:1000px;margin:24px auto;padding:0 16px;}"
        "table{border-collapse:collapse;width:100%;margin-top:12px;}"
        "th,td{border:1px solid #ccc;padding:6px 8px;text-align:left;}"
        "th{background:#f6f6f6;}"
        ".kpi{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0;}"
        ".card{border:1px solid #ddd;border-radius:10px;padding:10px 12px;min-width:180px;}"
        ".muted{color:#666;}"
        "</style>"
    )
    html.append("</head><body>")

    html.append(f"<h1>{title}</h1>")
    html.append(f"<p class='muted'>Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}Z</p>")

    html.append("<h2>Provenance</h2>")
    html.append("<ul>")
    html.append(f"<li><b>Tool</b>: {tool_name} {tool_version}</li>")
    html.append(f"<li><b>Timestamp (UTC)</b>: {timestamp_utc}</li>")
    html.append(f"<li><b>Release A</b>: {release_a}</li>")
    html.append(f"<li><b>Release B</b>: {release_b}</li>")
    html.append("</ul>")

    html.append("<h2>Overview</h2>")
    html.append("<div class='kpi'>")
    html.append(f"<div class='card'><b>Total entities changed</b><div>{total_all}</div></div>")
    html.append(f"<div class='card'><b>Added</b><div>{total_added}</div></div>")
    html.append(f"<div class='card'><b>Removed</b><div>{total_removed}</div></div>")
    html.append(f"<div class='card'><b>Changed</b><div>{total_changed}</div></div>")
    html.append("</div>")

    html.append("<h2>Summary plot</h2>")
    html.append("<img src='report.png' alt='Change counts plot' style='max-width:100%;height:auto;'>")

    html.append("<h2>Counts table</h2>")
    html.append("<table>")
    html.append("<tr><th>Entity type</th><th>Added</th><th>Removed</th><th>Changed</th><th>Total</th></tr>")
    for et in entity_types:
        a = counts[et].get("added", 0)
        r = counts[et].get("removed", 0)
        ch = counts[et].get("changed", 0)
        html.append(f"<tr><td>{et}</td><td>{a}</td><td>{r}</td><td>{ch}</td><td>{a+r+ch}</td></tr>")
    html.append("</table>")

    html.append("<h2>Artefacts</h2>")
    html.append("<ul>")
    html.append("<li><a href='changes.tsv'>changes.tsv</a></li>")
    html.append("<li><a href='summary.tsv'>summary.tsv</a></li>")
    html.append("<li><a href='run.json'>run.json</a></li>")
    html.append("</ul>")

    html.append("<h2>Detailed changes</h2>")
    html.append("<details>")
    html.append("<summary>Show changes.tsv table</summary>")
    html.append("<!details>")

    with open(os.path.join(outdir, "changes.tsv"), "r", encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        html.append("<div style='overflow-x:auto;'>")
        html.append("<table>")
        html.append("<tr>" + "".join(f"<th>{h}</th>" for h in header) + "</tr>")

        for line in fh:
            cols = line.rstrip("\n").split("\t")
            html.append("<tr>" + "".join(f"<td>{c}</td>" for c in cols) + "</tr>")

        html.append("</table>")
        html.append("</div>")

    html.append("</body></html>")

    report_path = os.path.join(outdir, "report.html")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(html))
        fh.write("\n")

    return report_path