"""
Summary Report Generator Module
Generates formatted markdown summary reports (table format) from parsed
monitoring data.
"""

from datetime import datetime


def categorize_by_threshold(entries, critical=90, warning=85):
    """Categorize entries into critical, warning, and stable groups."""
    critical_items = [e for e in entries if e.used_percent >= critical]
    warning_items = [e for e in entries if warning <= e.used_percent < critical]
    stable_items = [e for e in entries if e.used_percent < warning]
    return critical_items, warning_items, stable_items


def status_label(pct, critical, warning):
    """Return a status label with emoji based on thresholds."""
    if pct >= critical:
        return "🔴 Critical"
    elif pct >= warning:
        return "🟡 Warning"
    return "✅ Stable"


def _dedupe(entries, key):
    """Remove duplicate rows that share the same key (keeps highest %)."""
    seen = set()
    unique = []
    for e in sorted(entries, key=lambda x: x.used_percent, reverse=True):
        k = key(e)
        if k not in seen:
            seen.add(k)
            unique.append(e)
    return unique


def generate_tablespace_section(tablespaces):
    """Generate the tablespace section as a table."""
    lines = ["## 1. 🗄️ Tablespace Status\n"]

    if not tablespaces:
        lines.append("> No tablespace data available.\n")
        return '\n'.join(lines)

    rows = _dedupe(tablespaces, key=lambda e: (e.database, e.tablespace_name))
    rows.sort(key=lambda x: x.used_percent, reverse=True)

    lines.append("| Database | Tablespace | Used % | Status |")
    lines.append("|----------|------------|:------:|--------|")
    for ts in rows:
        lines.append(
            f"| {ts.database} | {ts.tablespace_name} | {ts.used_percent:.1f}% "
            f"| {status_label(ts.used_percent, 90, 85)} |"
        )
    lines.append("")
    return '\n'.join(lines)


def generate_diskgroup_section(diskgroups):
    """Generate the diskgroup (ASM) section as a table."""
    lines = ["## 2. 💽 Diskgroup (ASM) Status\n"]

    if not diskgroups:
        lines.append("> No diskgroup data available.\n")
        return '\n'.join(lines)

    rows = _dedupe(diskgroups, key=lambda e: (e.database, e.diskgroup_name))
    rows.sort(key=lambda x: x.used_percent, reverse=True)

    lines.append("| Database | Diskgroup | Used % | Status |")
    lines.append("|----------|-----------|:------:|--------|")
    for dg in rows:
        lines.append(
            f"| {dg.database} | {dg.diskgroup_name} | {dg.used_percent:.1f}% "
            f"| {status_label(dg.used_percent, 90, 70)} |"
        )
    lines.append("")
    return '\n'.join(lines)


def generate_mount_point_section(mount_points, section_title="PROD", section_num=3):
    """Generate a mount point section as a table."""
    lines = [f"## {section_num}. 💾 {section_title} Mount Point Status\n"]

    if not mount_points:
        lines.append("> No mount point data available.\n")
        return '\n'.join(lines)

    rows = _dedupe(mount_points, key=lambda e: (e.host, e.mount_point))
    rows.sort(key=lambda x: x.used_percent, reverse=True)

    has_host = any(mp.host for mp in rows)
    if has_host:
        lines.append("| Host | Mount Point | Used % | Status |")
        lines.append("|------|-------------|:------:|--------|")
        for mp in rows:
            lines.append(
                f"| {mp.host or '-'} | `{mp.mount_point}` | {mp.used_percent:.0f}% "
                f"| {status_label(mp.used_percent, 80, 65)} |"
            )
    else:
        lines.append("| Mount Point | Used % | Status |")
        lines.append("|-------------|:------:|--------|")
        for mp in rows:
            lines.append(
                f"| `{mp.mount_point}` | {mp.used_percent:.0f}% "
                f"| {status_label(mp.used_percent, 80, 65)} |"
            )
    lines.append("")
    return '\n'.join(lines)


def generate_alerts_section(data):
    """Generate the key alerts section as a table."""
    lines = ["# 🚨 Overall Key Alerts (Today)\n"]

    alerts = []

    for dg in _dedupe(data.diskgroups, key=lambda e: (e.database, e.diskgroup_name)):
        if dg.used_percent >= 90:
            alerts.append((f"{dg.database} {dg.diskgroup_name}", "Diskgroup",
                           dg.used_percent, "🔴 Critical"))

    for ts in _dedupe(data.tablespaces, key=lambda e: (e.database, e.tablespace_name)):
        if ts.used_percent >= 90:
            alerts.append((f"{ts.database} {ts.tablespace_name}", "Tablespace",
                           ts.used_percent, "🔴 Critical"))

    for mp in _dedupe(data.mount_points, key=lambda e: (e.host, e.mount_point)):
        if mp.used_percent >= 80:
            alerts.append((mp.mount_point, "Mount Point",
                           mp.used_percent, "🟠 Needs monitoring"))

    if not alerts:
        lines.append("> ✅ No critical alerts today\n")
        return '\n'.join(lines)

    alerts.sort(key=lambda x: x[2], reverse=True)
    lines.append("| Resource | Type | Used % | Status |")
    lines.append("|----------|------|:------:|--------|")
    for name, typ, pct, status in alerts:
        lines.append(f"| `{name}` | {typ} | {pct:.0f}% | {status} |")
    lines.append("")
    return '\n'.join(lines)


def generate_health_summary(data):
    """Generate the final health summary as a table."""
    lines = ["# ✅ Final Health Summary\n"]

    dev_tst_critical = any(
        ts.used_percent >= 90
        for ts in data.tablespaces
        if 'DEV' in ts.database or 'TST' in ts.database
    )
    prod_critical = any(
        ts.used_percent >= 90
        for ts in data.tablespaces
        if 'PRD' in ts.database
    ) or any(
        dg.used_percent >= 90
        for dg in data.diskgroups
        if 'PRD' in dg.database
    )

    lines.append("| Environment | Status |")
    lines.append("|-------------|--------|")
    lines.append(f"| DEV / TST | {'⚠️ Issues detected' if dev_tst_critical else '✅ Stable'} |")
    lines.append(f"| PROD | {'⚠️ Moderate risk areas exist' if prod_critical else '✅ Healthy'} |")

    all_critical = []
    for ts in data.tablespaces:
        if ts.used_percent >= 90:
            all_critical.append(f"{ts.database} ({ts.tablespace_name})")
    for dg in data.diskgroups:
        if dg.used_percent >= 90:
            all_critical.append(f"{dg.database} storage")

    if all_critical:
        lines.append(f"| Critical focus | 🔴 {', '.join(sorted(set(all_critical)))} |")

    lines.append("")
    return '\n'.join(lines)


def generate_full_report(data, report_date=None):
    """
    Generate the complete monitoring summary report.
    
    Args:
        data: MonitoringData object with parsed information
        report_date: Optional date string for the report header
    
    Returns:
        Complete markdown report string
    """
    if report_date is None:
        report_date = data.report_date or datetime.now().strftime('%d-%b-%Y')
    
    day_name = datetime.now().strftime('%A')
    
    report_lines = [
        f"# 📊 {day_name} Monitoring Summary ({report_date})\n",
    ]
    
    # Add sections
    report_lines.append(generate_tablespace_section(data.tablespaces))
    report_lines.append(generate_diskgroup_section(data.diskgroups))
    
    # Separate PROD and DEV/TST mount points
    prod_mounts = [mp for mp in data.mount_points if 'PRD' in mp.host.upper() or not mp.host]
    dev_mounts = [mp for mp in data.mount_points if 'DEV' in mp.host.upper() or 'TST' in mp.host.upper()]
    
    if prod_mounts or not dev_mounts:
        report_lines.append(generate_mount_point_section(prod_mounts or data.mount_points, "PROD", 3))
    if dev_mounts:
        report_lines.append(generate_mount_point_section(dev_mounts, "TST & DEV", 4))
    
    report_lines.append(generate_alerts_section(data))
    report_lines.append(generate_health_summary(data))
    
    return '\n'.join(report_lines)


# ============================================================================
#  HTML REPORT (professional, color-coded, grouped by environment)
# ============================================================================

# Status thresholds per metric: (critical, warning)
THRESHOLDS = {
    "tablespace": (90, 85),
    "diskgroup": (90, 70),
    "mount": (80, 65),
}

# Environment header colors
ENV_COLORS = {
    "PROD": "#c0392b",
    "QA/QTS": "#16a085",
    "TST": "#8e44ad",
    "DEV": "#2980b9",
    "OTHER": "#34495e",
}

# Palette for color-coding database / resource names (stable hashing)
DB_PALETTE = [
    "#1f618d", "#117864", "#7d6608", "#6c3483",
    "#a04000", "#1a5276", "#922b21", "#0e6655",
]


def infer_environment(text):
    """Classify a database name, host, or mount path into an environment."""
    t = (text or "").upper()
    if "PRD" in t or "PROD" in t:
        return "PROD"
    if "QTS" in t or "QA" in t:
        return "QA/QTS"
    if "TST" in t or "TEST" in t:
        return "TST"
    if "DEV" in t:
        return "DEV"
    return "OTHER"


def db_color(name):
    """Deterministic color for a database/resource name."""
    if not name:
        return "#34495e"
    idx = sum(ord(c) for c in str(name)) % len(DB_PALETTE)
    return DB_PALETTE[idx]


def status_style(pct, metric):
    """Return (label, text_color, bg_color) for a usage percentage."""
    critical, warning = THRESHOLDS[metric]
    if pct >= critical:
        return ("CRITICAL", "#ffffff", "#c0392b")
    elif pct >= warning:
        return ("WARNING", "#7d5a00", "#fce8b6")
    return ("OK", "#1e6b3a", "#cdefd8")


def _badge(label, text_color, bg_color):
    """Render a colored status badge cell content."""
    return (
        f'<span style="display:inline-block;padding:3px 10px;border-radius:12px;'
        f'font-size:11px;font-weight:bold;color:{text_color};'
        f'background-color:{bg_color};">{label}</span>'
    )


def _bar(pct, metric):
    """Render a small horizontal usage bar."""
    _, _, bar_color = status_style(pct, metric)
    width = max(2, min(100, int(pct)))
    return (
        f'<table cellpadding="0" cellspacing="0" border="0" width="100" '
        f'style="background:#eceff1;border-radius:4px;"><tr>'
        f'<td style="height:10px;width:{width}%;background:{bar_color};'
        f'border-radius:4px;font-size:0;line-height:0;">&nbsp;</td>'
        f'<td style="font-size:0;line-height:0;">&nbsp;</td></tr></table>'
    )


def _group_by_environment(data):
    """Group all parsed entries by inferred environment."""
    groups = {}

    for ts in _dedupe(data.tablespaces, key=lambda e: (e.database, e.tablespace_name)):
        env = infer_environment(ts.database)
        groups.setdefault(env, {"tablespaces": [], "diskgroups": [], "mounts": []})
        groups[env]["tablespaces"].append(ts)

    for dg in _dedupe(data.diskgroups, key=lambda e: (e.database, e.diskgroup_name)):
        env = infer_environment(dg.database)
        groups.setdefault(env, {"tablespaces": [], "diskgroups": [], "mounts": []})
        groups[env]["diskgroups"].append(dg)

    for mp in _dedupe(data.mount_points, key=lambda e: (e.host, e.mount_point)):
        env = infer_environment(mp.host or mp.mount_point)
        groups.setdefault(env, {"tablespaces": [], "diskgroups": [], "mounts": []})
        groups[env]["mounts"].append(mp)

    return groups


def _summary_counts(data):
    """Count critical / warning / ok across all metrics."""
    counts = {"CRITICAL": 0, "WARNING": 0, "OK": 0}
    for ts in data.tablespaces:
        counts[status_style(ts.used_percent, "tablespace")[0]] += 1
    for dg in data.diskgroups:
        counts[status_style(dg.used_percent, "diskgroup")[0]] += 1
    for mp in data.mount_points:
        counts[status_style(mp.used_percent, "mount")[0]] += 1
    return counts


def _metric_table(title, headers, rows_html):
    """Wrap a metric table with a title and header row."""
    if not rows_html:
        return ""
    head_cells = "".join(
        f'<th align="left" style="padding:8px 10px;font-size:12px;color:#ffffff;'
        f'background:#34495e;border:1px solid #2c3e50;">{h}</th>'
        for h in headers
    )
    return (
        f'<p style="margin:14px 0 6px;font-size:13px;font-weight:bold;color:#2c3e50;">{title}</p>'
        f'<table cellpadding="0" cellspacing="0" border="0" width="100%" '
        f'style="border-collapse:collapse;font-size:12px;">'
        f'<tr>{head_cells}</tr>{rows_html}</table>'
    )


def _row(cells):
    tds = "".join(
        f'<td style="padding:7px 10px;border:1px solid #e0e0e0;{style}">{val}</td>'
        for val, style in cells
    )
    return f"<tr>{tds}</tr>"


def generate_html_report(data, report_date=None):
    """Generate a professional, color-coded HTML report grouped by environment."""
    if report_date is None:
        report_date = data.report_date or datetime.now().strftime("%d-%b-%Y")
    day_name = datetime.now().strftime("%A")

    counts = _summary_counts(data)
    groups = _group_by_environment(data)

    # ---- Header ----
    html = [
        '<html><body style="margin:0;padding:0;background:#f4f6f8;'
        'font-family:Segoe UI,Calibri,Arial,sans-serif;color:#2c3e50;">',
        '<table cellpadding="0" cellspacing="0" border="0" width="100%" '
        'style="background:#f4f6f8;padding:20px 0;"><tr><td align="center">',
        '<table cellpadding="0" cellspacing="0" border="0" width="780" '
        'style="background:#ffffff;border-radius:8px;overflow:hidden;'
        'box-shadow:0 1px 4px rgba(0,0,0,0.1);">',
        # Title bar
        '<tr><td style="background:#1a5276;padding:22px 28px;">'
        '<div style="font-size:22px;font-weight:bold;color:#ffffff;">'
        f'&#128202; {day_name} Monitoring Summary</div>'
        f'<div style="font-size:13px;color:#aed6f1;margin-top:4px;">Report Date: {report_date}</div>'
        '</td></tr>',
    ]

    # ---- Summary cards ----
    def card(label, value, color):
        return (
            f'<td width="33%" align="center" style="padding:6px;">'
            f'<table cellpadding="0" cellspacing="0" border="0" width="100%" '
            f'style="background:{color}10;border:1px solid {color};border-radius:6px;">'
            f'<tr><td align="center" style="padding:14px;">'
            f'<div style="font-size:26px;font-weight:bold;color:{color};">{value}</div>'
            f'<div style="font-size:12px;color:{color};text-transform:uppercase;'
            f'letter-spacing:1px;">{label}</div></td></tr></table></td>'
        )

    html.append(
        '<tr><td style="padding:18px 22px 4px;">'
        '<table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>'
        + card("Critical", counts["CRITICAL"], "#c0392b")
        + card("Warning", counts["WARNING"], "#e67e22")
        + card("Healthy", counts["OK"], "#27ae60")
        + '</tr></table></td></tr>'
    )

    # ---- Per-environment sections ----
    env_order = ["PROD", "QA/QTS", "TST", "DEV", "OTHER"]
    sorted_envs = [e for e in env_order if e in groups] + [
        e for e in groups if e not in env_order
    ]

    for env in sorted_envs:
        g = groups[env]
        env_color = ENV_COLORS.get(env, "#34495e")

        html.append(
            '<tr><td style="padding:10px 22px 0;">'
            f'<div style="background:{env_color};color:#ffffff;padding:9px 14px;'
            f'border-radius:5px;font-size:15px;font-weight:bold;margin-top:10px;">'
            f'&#128193; {env} Environment</div></td></tr>'
        )

        body_parts = []

        # Tablespaces
        ts_rows = ""
        for ts in sorted(g["tablespaces"], key=lambda x: x.used_percent, reverse=True):
            label, tc, bc = status_style(ts.used_percent, "tablespace")
            ts_rows += _row([
                (f'<b style="color:{db_color(ts.database)};">{ts.database}</b>', ""),
                (ts.tablespace_name, ""),
                (f"{ts.used_percent:.1f}%", "text-align:center;font-weight:bold;"),
                (_bar(ts.used_percent, "tablespace"), "width:110px;"),
                (_badge(label, tc, bc), "text-align:center;"),
            ])
        body_parts.append(_metric_table(
            "&#128451; Tablespaces",
            ["Database", "Tablespace", "Used %", "Usage", "Status"],
            ts_rows,
        ))

        # Diskgroups
        dg_rows = ""
        for dg in sorted(g["diskgroups"], key=lambda x: x.used_percent, reverse=True):
            label, tc, bc = status_style(dg.used_percent, "diskgroup")
            dg_rows += _row([
                (f'<b style="color:{db_color(dg.database)};">{dg.database}</b>', ""),
                (dg.diskgroup_name, ""),
                (f"{dg.used_percent:.1f}%", "text-align:center;font-weight:bold;"),
                (_bar(dg.used_percent, "diskgroup"), "width:110px;"),
                (_badge(label, tc, bc), "text-align:center;"),
            ])
        body_parts.append(_metric_table(
            "&#128189; Diskgroups (ASM)",
            ["Database", "Diskgroup", "Used %", "Usage", "Status"],
            dg_rows,
        ))

        # Mount points
        mp_rows = ""
        for mp in sorted(g["mounts"], key=lambda x: x.used_percent, reverse=True):
            label, tc, bc = status_style(mp.used_percent, "mount")
            mp_rows += _row([
                (f'<code style="color:#2c3e50;">{mp.mount_point}</code>', ""),
                (f"{mp.used_percent:.0f}%", "text-align:center;font-weight:bold;"),
                (_bar(mp.used_percent, "mount"), "width:110px;"),
                (_badge(label, tc, bc), "text-align:center;"),
            ])
        body_parts.append(_metric_table(
            "&#128190; Mount Points",
            ["Mount Point", "Used %", "Usage", "Status"],
            mp_rows,
        ))

        section_body = "".join(p for p in body_parts if p) or \
            '<p style="font-size:12px;color:#888;">No data for this environment.</p>'
        html.append(f'<tr><td style="padding:4px 22px 8px;">{section_body}</td></tr>')

    # ---- Critical alerts callout ----
    alerts = []
    for dg in data.diskgroups:
        if status_style(dg.used_percent, "diskgroup")[0] == "CRITICAL":
            alerts.append((f"{dg.database} / {dg.diskgroup_name}", "Diskgroup", dg.used_percent))
    for ts in data.tablespaces:
        if status_style(ts.used_percent, "tablespace")[0] == "CRITICAL":
            alerts.append((f"{ts.database} / {ts.tablespace_name}", "Tablespace", ts.used_percent))
    for mp in _dedupe(data.mount_points, key=lambda e: (e.host, e.mount_point)):
        if status_style(mp.used_percent, "mount")[0] == "CRITICAL":
            alerts.append((mp.mount_point, "Mount Point", mp.used_percent))

    if alerts:
        alert_rows = ""
        for name, typ, pct in sorted(alerts, key=lambda x: x[2], reverse=True):
            alert_rows += _row([
                (f'<b>{name}</b>', "color:#c0392b;"),
                (typ, ""),
                (f"{pct:.0f}%", "text-align:center;font-weight:bold;color:#c0392b;"),
            ])
        html.append(
            '<tr><td style="padding:6px 22px 14px;">'
            '<div style="background:#fdecea;border-left:4px solid #c0392b;'
            'border-radius:4px;padding:10px 14px;">'
            '<div style="font-size:14px;font-weight:bold;color:#c0392b;margin-bottom:6px;">'
            '&#128680; Critical Issues Requiring Attention</div>'
            '<table cellpadding="0" cellspacing="0" border="0" width="100%" '
            'style="border-collapse:collapse;font-size:12px;">'
            + alert_rows + '</table></div></td></tr>'
        )
    else:
        html.append(
            '<tr><td style="padding:6px 22px 14px;">'
            '<div style="background:#eafaf1;border-left:4px solid #27ae60;'
            'border-radius:4px;padding:10px 14px;font-size:13px;color:#1e6b3a;">'
            '&#9989; No critical issues detected. All monitored resources are within healthy limits.'
            '</div></td></tr>'
        )

    # ---- Footer ----
    html.append(
        '<tr><td style="background:#f4f6f8;padding:14px 22px;border-top:1px solid #e0e0e0;'
        'font-size:11px;color:#95a5a6;text-align:center;">'
        'Automated report generated by the Friday Monitoring Summary Agent &middot; '
        f'{datetime.now().strftime("%d-%b-%Y %H:%M")}'
        '</td></tr>'
    )

    html.append('</table></td></tr></table></body></html>')
    return "".join(html)

