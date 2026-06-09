"""
dashboard.py  —  Friday Monitoring Auto-Scanner
================================================
Run this script on Windows with Outlook open.

    python dashboard.py                        # scan today / last Friday
    python dashboard.py --days-back 14         # wider look-back
    python dashboard.py --folder "My Folder"   # custom Outlook folder
    python dashboard.py --no-browser           # save HTML, don't open browser

It will:
  1. Connect to Outlook via COM/MAPI
  2. Pull the latest tablespace, diskgroup, and mount-point emails
  3. Parse all data automatically
  4. Generate a colour-coded HTML dashboard (same visual as Claude output)
  5. Open it instantly in your default browser
  6. Optionally email the report
"""

import argparse
import os
import re
import sys
import webbrowser
from collections import defaultdict
from datetime import datetime

# ── make sure the agent modules are importable ────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    from outlook_reader import (
        connect_outlook,
        get_folder,
        get_emails_by_subject,
        send_email,
    )
    from email_parser import parse_monitoring_emails
except ImportError as exc:
    print(f"\n  ❌ Import error: {exc}")
    print("  Make sure outlook_reader.py and email_parser.py are in the same folder.")
    sys.exit(1)


# ── config ────────────────────────────────────────────────────────────────────
DEFAULT_FOLDER   = "Friday Monitoring"
RECIPIENT_EMAIL  = "ajay.kumar@incedoinc.com"
MONITORING_KEYWORDS = [
    "tablespace", "diskgroup", "mount point", "monitoring",
    "disk", "ASM", "filesystem", "Thursday-Friday", "Friday",
]

# severity thresholds
TS_CRIT,  TS_WARN  = 90, 85
DG_CRIT,  DG_WARN  = 90, 70
MP_CRIT,  MP_WARN  = 80, 65


# ── helpers ───────────────────────────────────────────────────────────────────
def _env(name):
    t = (name or "").upper()
    if "PRD" in t or "PROD" in t: return "PROD"
    if "QTS" in t or "QA"  in t:  return "QA/QTS"
    if "TST" in t or "TEST" in t: return "TST"
    if "DEV" in t:                 return "DEV"
    return "OTHER"

def _status(pct, crit, warn):
    if pct >= crit: return "CRITICAL", "#ffffff", "#c0392b"
    if pct >= warn: return "WARNING",  "#7d5a00", "#fce8b6"
    return "OK", "#1e6b3a", "#cdefd8"

def _bar(pct, crit, warn):
    _, _, bc = _status(pct, crit, warn)
    w = max(2, min(100, int(pct)))
    return (
        f'<div style="background:#e8eaed;border-radius:4px;height:8px;width:100px;">'
        f'<div style="height:8px;width:{w}%;background:{bc};border-radius:4px;"></div></div>'
    )

def _badge(label, tc, bc):
    return (
        f'<span style="display:inline-block;padding:3px 10px;border-radius:10px;'
        f'font-size:11px;font-weight:600;color:{tc};background:{bc};">{label}</span>'
    )

def _dedupe(entries, key):
    seen, out = set(), []
    for e in sorted(entries, key=lambda x: x.used_percent, reverse=True):
        k = key(e)
        if k not in seen:
            seen.add(k); out.append(e)
    return out

def _normalize(subject):
    s = subject.lower()
    s = re.sub(r'\d{1,2}[-/ ]*[a-z]{3,}[-/ ]*\d{2,4}', '', s)
    s = re.sub(r'\d{4}-\d{2}-\d{2}', '', s)
    s = re.sub(r'[-_\s]+', ' ', s).strip()
    return s

def deduplicate_latest(emails):
    seen, out = set(), []
    for e in sorted(emails, key=lambda x: x['received_time'], reverse=True):
        k = _normalize(e['subject'])
        if k not in seen:
            seen.add(k); out.append(e)
    return out


# ── HTML dashboard builder ────────────────────────────────────────────────────
ENV_COLORS = {
    "PROD":   "#c0392b",
    "QA/QTS": "#16a085",
    "TST":    "#8e44ad",
    "DEV":    "#2980b9",
    "OTHER":  "#34495e",
}

def _th(*cols):
    cells = "".join(
        f'<th style="padding:8px 10px;text-align:left;font-size:11px;'
        f'color:#fff;background:#34495e;border:1px solid #2c3e50;">{c}</th>'
        for c in cols
    )
    return f"<tr>{cells}</tr>"

def _td(*pairs):
    cells = "".join(
        f'<td style="padding:7px 10px;border:1px solid #e0e0e0;{st}">{val}</td>'
        for val, st in pairs
    )
    return f"<tr>{cells}</tr>"

def _section_table(title, header_row, body_rows):
    if not body_rows:
        return ""
    return (
        f'<p style="margin:14px 0 6px;font-size:13px;font-weight:600;color:#2c3e50;">{title}</p>'
        f'<table cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:12px;width:100%;">'
        f'{header_row}{"".join(body_rows)}</table>'
    )

def build_html(data, report_date, emails_found):
    day_name = datetime.now().strftime("%A")

    # ── count totals ──────────────────────────────────────────────────────────
    def cnt(entries, crit, warn):
        c = w = ok = 0
        for e in entries:
            s, _, _ = _status(e.used_percent, crit, warn)
            if s == "CRITICAL": c += 1
            elif s == "WARNING": w += 1
            else: ok += 1
        return c, w, ok

    tc, tw, tok = cnt(data.tablespaces, TS_CRIT, TS_WARN)
    dc, dw, dok = cnt(data.diskgroups,  DG_CRIT, DG_WARN)
    mc, mw, mok = cnt(data.mount_points, MP_CRIT, MP_WARN)
    total_crit = tc + dc + mc
    total_warn = tw + dw + mw
    total_ok   = tok + dok + mok

    # ── group by environment ──────────────────────────────────────────────────
    groups = {}
    for ts in _dedupe(data.tablespaces, key=lambda e: (e.database, e.tablespace_name)):
        g = _env(ts.database)
        groups.setdefault(g, {"ts": [], "dg": [], "mp": []})["ts"].append(ts)
    for dg in _dedupe(data.diskgroups, key=lambda e: (e.database, e.diskgroup_name)):
        g = _env(dg.database)
        groups.setdefault(g, {"ts": [], "dg": [], "mp": []})["dg"].append(dg)
    for mp in _dedupe(data.mount_points, key=lambda e: (e.host, e.mount_point)):
        g = _env(mp.host or mp.mount_point)
        groups.setdefault(g, {"ts": [], "dg": [], "mp": []})["mp"].append(mp)

    env_order = ["PROD", "QA/QTS", "TST", "DEV", "OTHER"]
    sorted_envs = [e for e in env_order if e in groups] + [e for e in groups if e not in env_order]

    # ── helper: env banner row inside a table ─────────────────────────────────
    def _env_banner(env, colspan):
        ecol = ENV_COLORS.get(env, "#34495e")
        return (
            f'<tr><td colspan="{colspan}" style="padding:8px 10px 5px;'
            f'background:{ecol};color:#fff;font-size:12px;font-weight:700;'
            f'border:1px solid {ecol};letter-spacing:0.5px;">'
            f'&#128193; {env} Environment</td></tr>'
        )

    def _db_banner(db_name, colspan):
        return (
            f'<tr><td colspan="{colspan}" style="padding:5px 10px 4px;background:#eaf0fb;'
            f'font-size:11px;font-weight:700;color:#1a5276;border:1px solid #c5d5ea;'
            f'letter-spacing:0.4px;">&#128194; {db_name}</td></tr>'
        )

    # ── BUILD: ALL TABLESPACES (env → db → rows) ──────────────────────────────
    all_ts_rows = []
    for env in sorted_envs:
        ts_list = groups[env]["ts"]
        if not ts_list:
            continue
        all_ts_rows.append(_env_banner(env, 5))
        ts_by_db = defaultdict(list)
        for ts in ts_list:
            ts_by_db[ts.database].append(ts)
        for db_name in sorted(ts_by_db.keys()):
            all_ts_rows.append(_db_banner(db_name, 5))
            for ts in sorted(ts_by_db[db_name], key=lambda x: x.used_percent, reverse=True):
                all_ts_rows.append(_td(
                    (f'<b style="color:#1a5276">{ts.database}</b>', ""),
                    (ts.tablespace_name, "font-family:monospace;font-size:11px;"),
                    (f"{ts.used_percent:.1f}%", "text-align:center;font-weight:600;"),
                    (_bar(ts.used_percent, TS_CRIT, TS_WARN), "width:110px;"),
                    (_badge(*_status(ts.used_percent, TS_CRIT, TS_WARN)), "text-align:center;"),
                ))

    ts_section_html = _section_table(
        "&#128451; Tablespaces",
        _th("Database", "Tablespace", "Used %", "Usage", "Status"),
        all_ts_rows,
    )

    # ── BUILD: ALL DISKGROUPS (env → db → rows) ───────────────────────────────
    all_dg_rows = []
    for env in sorted_envs:
        dg_list = groups[env]["dg"]
        if not dg_list:
            continue
        all_dg_rows.append(_env_banner(env, 5))
        dg_by_db = defaultdict(list)
        for dg in dg_list:
            dg_by_db[dg.database].append(dg)
        for db_name in sorted(dg_by_db.keys()):
            all_dg_rows.append(_db_banner(db_name, 5))
            for dg in sorted(dg_by_db[db_name], key=lambda x: x.used_percent, reverse=True):
                all_dg_rows.append(_td(
                    (f'<b style="color:#1a5276">{dg.database}</b>', ""),
                    (dg.diskgroup_name, ""),
                    (f"{dg.used_percent:.1f}%", "text-align:center;font-weight:600;"),
                    (_bar(dg.used_percent, DG_CRIT, DG_WARN), "width:110px;"),
                    (_badge(*_status(dg.used_percent, DG_CRIT, DG_WARN)), "text-align:center;"),
                ))

    dg_section_html = _section_table(
        "&#128189; Diskgroups (ASM)",
        _th("Database", "Diskgroup", "Used %", "Usage", "Status"),
        all_dg_rows,
    )

    # ── BUILD: ALL MOUNT POINTS (env → host → rows) ───────────────────────────
    all_mp_rows = []
    for env in sorted_envs:
        mp_list = groups[env]["mp"]
        if not mp_list:
            continue
        all_mp_rows.append(_env_banner(env, 4))
        mp_by_host = defaultdict(list)
        for mp in mp_list:
            host_key = mp.host if (mp.host and mp.host.strip()) else "Unknown Host"
            mp_by_host[host_key].append(mp)
        for host_name in sorted(mp_by_host.keys()):
            all_mp_rows.append(_db_banner(host_name, 4))
            for mp in sorted(mp_by_host[host_name], key=lambda x: x.used_percent, reverse=True):
                all_mp_rows.append(_td(
                    (f'<code style="color:#2c3e50;">{mp.mount_point}</code>', ""),
                    (f"{mp.used_percent:.0f}%", "text-align:center;font-weight:600;"),
                    (_bar(mp.used_percent, MP_CRIT, MP_WARN), "width:110px;"),
                    (_badge(*_status(mp.used_percent, MP_CRIT, MP_WARN)), "text-align:center;"),
                ))

    mp_section_html = _section_table(
        "&#128190; Mount Points",
        _th("Mount Point", "Used %", "Usage", "Status"),
        all_mp_rows,
    )

    env_html = f"""
    <tr><td style="padding:10px 22px 4px;">
      {ts_section_html}
      {dg_section_html}
      {mp_section_html}
    </td></tr>
    """

    # ── critical alert callout ────────────────────────────────────────────────
    alerts = []
    for dg in _dedupe(data.diskgroups, key=lambda e: (e.database, e.diskgroup_name)):
        if dg.used_percent >= DG_CRIT:
            alerts.append((f"{dg.database} / {dg.diskgroup_name}", "Diskgroup", dg.used_percent))
    for ts in _dedupe(data.tablespaces, key=lambda e: (e.database, e.tablespace_name)):
        if ts.used_percent >= TS_CRIT:
            alerts.append((f"{ts.database} / {ts.tablespace_name}", "Tablespace", ts.used_percent))
    for mp in _dedupe(data.mount_points, key=lambda e: (e.host, e.mount_point)):
        if mp.used_percent >= MP_CRIT:
            alerts.append((mp.mount_point, "Mount Point", mp.used_percent))

    if alerts:
        alert_rows = "".join(
            _td(
                (f'<b>{name}</b>', "color:#c0392b;"),
                (typ, ""),
                (f"{pct:.0f}%", "text-align:center;font-weight:600;color:#c0392b;"),
            )
            for name, typ, pct in sorted(alerts, key=lambda x: x[2], reverse=True)
        )
        alert_box = f"""
        <tr><td style="padding:6px 22px 14px;">
          <div style="background:#fdecea;border-left:4px solid #c0392b;border-radius:4px;padding:12px 16px;">
            <div style="font-size:14px;font-weight:600;color:#c0392b;margin-bottom:8px;">
              &#128680; Critical Issues Requiring Immediate Attention
            </div>
            <table cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:12px;width:100%;">
              {_th("Resource", "Type", "Used %")}{alert_rows}
            </table>
          </div>
        </td></tr>"""
    else:
        alert_box = """
        <tr><td style="padding:6px 22px 14px;">
          <div style="background:#eafaf1;border-left:4px solid #27ae60;border-radius:4px;padding:12px 16px;
               font-size:13px;color:#1e6b3a;">
            &#9989; No critical issues detected. All monitored resources are within healthy limits.
          </div>
        </td></tr>"""

    # ── email list ────────────────────────────────────────────────────────────
    email_list = "".join(
        f'<li style="margin:2px 0;">[{e["received_time"].strftime("%d-%b %H:%M")}] '
        f'<b>{e["subject"]}</b> — from {e.get("sender","")}</li>'
        for e in emails_found
    )

    now_str = datetime.now().strftime("%d-%b-%Y %H:%M")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Friday Monitoring Dashboard — {report_date}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background:#f4f6f8; font-family: Segoe UI, Calibri, Arial, sans-serif;
            color:#2c3e50; font-size:13px; }}
    a {{ color:#2980b9; }}
  </style>
</head>
<body>
<table cellpadding="0" cellspacing="0" border="0" width="100%"
       style="background:#f4f6f8;padding:24px 0;">
  <tr><td align="center">
  <table cellpadding="0" cellspacing="0" border="0" width="820"
         style="background:#fff;border-radius:8px;overflow:hidden;
                box-shadow:0 1px 6px rgba(0,0,0,0.12);">

    <!-- title bar -->
    <tr><td style="background:#1a5276;padding:24px 28px;">
      <div style="font-size:24px;font-weight:700;color:#fff;">
        &#128202; {day_name} Monitoring Dashboard
      </div>
      <div style="font-size:13px;color:#aed6f1;margin-top:4px;">
        Report date: {report_date} &nbsp;|&nbsp; Generated: {now_str}
      </div>
    </td></tr>

    <!-- summary cards -->
    <tr><td style="padding:18px 22px 4px;">
      <table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
        <td width="33%" style="padding:6px;">
          <table width="100%" style="background:#c0392b10;border:1px solid #c0392b;border-radius:6px;">
            <tr><td align="center" style="padding:14px;">
              <div style="font-size:28px;font-weight:700;color:#c0392b;">{total_crit}</div>
              <div style="font-size:11px;color:#c0392b;text-transform:uppercase;letter-spacing:1px;">Critical</div>
            </td></tr></table></td>
        <td width="33%" style="padding:6px;">
          <table width="100%" style="background:#e67e2210;border:1px solid #e67e22;border-radius:6px;">
            <tr><td align="center" style="padding:14px;">
              <div style="font-size:28px;font-weight:700;color:#e67e22;">{total_warn}</div>
              <div style="font-size:11px;color:#e67e22;text-transform:uppercase;letter-spacing:1px;">Warning</div>
            </td></tr></table></td>
        <td width="33%" style="padding:6px;">
          <table width="100%" style="background:#27ae6010;border:1px solid #27ae60;border-radius:6px;">
            <tr><td align="center" style="padding:14px;">
              <div style="font-size:28px;font-weight:700;color:#27ae60;">{total_ok}</div>
              <div style="font-size:11px;color:#27ae60;text-transform:uppercase;letter-spacing:1px;">Healthy</div>
            </td></tr></table></td>
      </tr></table>
    </td></tr>

    <!-- emails scanned -->
    <tr><td style="padding:8px 22px 0;">
      <details style="font-size:12px;color:#555;border:1px solid #ddd;
                      border-radius:4px;padding:8px 12px;background:#fafafa;">
        <summary style="cursor:pointer;font-weight:600;color:#2c3e50;">
          &#128231; {len(emails_found)} email(s) scanned from Outlook
        </summary>
        <ul style="margin:8px 0 0 16px;line-height:1.8;">{email_list}</ul>
      </details>
    </td></tr>

    <!-- environment sections -->
    {env_html}

    <!-- critical alerts -->
    {alert_box}

    <!-- footer -->
    <tr><td style="background:#f4f6f8;padding:14px 22px;border-top:1px solid #e0e0e0;
                   font-size:11px;color:#95a5a6;text-align:center;">
      Auto-generated by Friday Monitoring Dashboard &middot; {now_str}
    </td></tr>

  </table>
  </td></tr>
</table>
</body>
</html>"""


# ── main ──────────────────────────────────────────────────────────────────────
def run(folder_name, days_back, output_file, send_to, open_browser):
    print("=" * 60)
    print("  📊 Friday Monitoring Auto-Scanner")
    print("=" * 60)

    # 1. Connect
    print("\n[1/4] Connecting to Outlook...")
    try:
        namespace = connect_outlook()
        print("  ✅ Connected")
    except Exception as e:
        print(f"  ❌ {e}\n  Make sure Outlook is open.")
        sys.exit(1)

    # 2. Get folder
    print(f"\n[2/4] Opening folder '{folder_name}'...")
    try:
        folder = get_folder(namespace, folder_name)
        print(f"  ✅ {folder.Name} ({folder.Items.Count} items)")
    except FileNotFoundError as e:
        print(f"  ❌ {e}")
        sys.exit(1)

    # 3. Fetch & deduplicate emails
    print(f"\n[3/4] Fetching emails (last {days_back} days)...")
    emails = get_emails_by_subject(folder, MONITORING_KEYWORDS, days_back)
    if not emails:
        print("  ⚠️  No monitoring emails found. Try --days-back 14.")
        sys.exit(0)
    emails = deduplicate_latest(emails)
    print(f"  ✅ {len(emails)} unique email(s):")
    for i, e in enumerate(emails, 1):
        print(f"     {i}. [{e['received_time'].strftime('%d-%b %H:%M')}] {e['subject']}")

    # 4. Parse
    print("\n[4/4] Parsing monitoring data...")
    data = parse_monitoring_emails(emails)
    print(f"  ✅ {len(data.tablespaces)} tablespace entries")
    print(f"  ✅ {len(data.diskgroups)} diskgroup entries")
    print(f"  ✅ {len(data.mount_points)} mount point entries")

    # 5. Build HTML
    report_date = datetime.now().strftime("%d-%b-%Y")
    html = build_html(data, report_date, emails)

    # 6. Save
    if not output_file:
        output_file = os.path.join(HERE, f"monitoring_dashboard_{datetime.now().strftime('%Y%m%d')}.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n  💾 Dashboard saved: {output_file}")

    # 7. Open browser
    if open_browser:
        webbrowser.open(f"file:///{output_file.replace(os.sep, '/')}")
        print("  🌐 Opened in browser")

    # 8. Email (optional)
    if send_to:
        print(f"\n  📧 Sending to {send_to}...")
        try:
            subject = f"📊 {datetime.now().strftime('%A')} Monitoring Dashboard ({report_date})"
            send_email(send_to, subject, body_markdown="", body_html=html)
            print("  ✅ Email sent")
        except Exception as e:
            print(f"  ❌ Email failed: {e}")

    print("\n  Done ✅")


def main():
    p = argparse.ArgumentParser(description="Friday Monitoring Auto-Scanner")
    p.add_argument("--folder",     "-f", default=DEFAULT_FOLDER,
                   help=f'Outlook folder (default: "{DEFAULT_FOLDER}")')
    p.add_argument("--days-back",        type=int, default=7,
                   help="Days to look back for emails (default: 7)")
    p.add_argument("--output",     "-o", default=None,
                   help="Output HTML file path")
    p.add_argument("--send-to",    "-s", default=None,
                   help="Send report to this email address")
    p.add_argument("--email",            action="store_true",
                   help=f"Auto-send to {RECIPIENT_EMAIL}")
    p.add_argument("--no-browser",       action="store_true",
                   help="Don't open browser after generating")
    args = p.parse_args()

    send_to = None
    if args.send_to:
        send_to = args.send_to
    elif args.email:
        send_to = RECIPIENT_EMAIL

    run(
        folder_name  = args.folder,
        days_back    = args.days_back,
        output_file  = args.output,
        send_to      = send_to,
        open_browser = not args.no_browser,
    )

if __name__ == "__main__":
    main()
