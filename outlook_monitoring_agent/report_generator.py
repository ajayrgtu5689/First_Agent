"""
Summary Report Generator Module
Generates formatted markdown summary reports from parsed monitoring data.
"""

from datetime import datetime


def categorize_by_threshold(entries, critical=90, warning=85):
    """Categorize entries into critical, warning, and stable groups."""
    critical_items = [e for e in entries if e.used_percent >= critical]
    warning_items = [e for e in entries if warning <= e.used_percent < critical]
    stable_items = [e for e in entries if e.used_percent < warning]
    return critical_items, warning_items, stable_items


def generate_tablespace_section(tablespaces):
    """Generate the tablespace section of the report."""
    if not tablespaces:
        return "## 1. 🗄️ Tablespace Status\n\n> No tablespace data available.\n\n"
    
    critical, warning, stable = categorize_by_threshold(tablespaces, critical=90, warning=85)
    
    lines = ["## 1. 🗄️ Tablespace Status\n"]
    
    # Critical
    lines.append("### 🔴 High Utilization (Critical/Watch)\n")
    if critical:
        # Group by database
        db_groups = {}
        for ts in sorted(critical, key=lambda x: x.used_percent, reverse=True):
            db_groups.setdefault(ts.database, []).append(ts)
        
        for db, items in db_groups.items():
            lines.append(f"* **{db}**")
            for ts in items:
                lines.append(f"  * {ts.tablespace_name} → **{ts.used_percent:.1f}% used**")
    else:
        lines.append("* None ✅")
    
    lines.append("")
    
    # Warning
    lines.append("### 🟡 Moderate Utilization (85–90%)\n")
    if warning:
        for ts in sorted(warning, key=lambda x: x.used_percent, reverse=True):
            lines.append(f"* {ts.tablespace_name} ({ts.database}) → ~{ts.used_percent:.1f}%")
    else:
        lines.append("* None ✅")
    
    lines.append("")
    
    # Stable
    lines.append("### ✅ Stable\n")
    if stable:
        lines.append(f"* {len(stable)} tablespaces below 85% — all within healthy limits")
        # Show a few notable ones
        notable = [ts for ts in stable if ts.used_percent >= 80]
        if notable:
            lines.append(f"* Approaching threshold: {', '.join(f'{ts.tablespace_name} ({ts.used_percent:.0f}%)' for ts in notable[:5])}")
    else:
        lines.append("* No stable tablespaces found")
    
    lines.append("")
    
    # Observation
    if critical:
        lines.append("👉 **Observation:**  ")
        dbs = set(ts.database for ts in critical)
        lines.append(
            f"Multiple tablespaces are **approaching or crossing 90%**, "
            f"especially in **{', '.join(dbs)}** environments — "
            f"capacity planning or cleanup may be required.\n"
        )
    
    return '\n'.join(lines)


def generate_diskgroup_section(diskgroups):
    """Generate the diskgroup (ASM) section of the report."""
    if not diskgroups:
        return "## 2. 💽 Diskgroup (ASM) Status\n\n> No diskgroup data available.\n\n"
    
    critical, warning, stable = categorize_by_threshold(diskgroups, critical=90, warning=70)
    
    lines = ["## 2. 💽 Diskgroup (ASM) Status\n"]
    
    # Critical
    lines.append("### 🔴 Critical\n")
    if critical:
        for dg in sorted(critical, key=lambda x: x.used_percent, reverse=True):
            lines.append(f"* **{dg.database} {dg.diskgroup_name} diskgroup → ~{dg.used_percent:.2f}% used**")
    else:
        lines.append("* None ✅")
    
    lines.append("")
    
    # Warning/Moderate
    lines.append("### 🟡 Moderate Usage\n")
    if warning:
        for dg in sorted(warning, key=lambda x: x.used_percent, reverse=True):
            lines.append(f"* {dg.database} {dg.diskgroup_name} → ~{dg.used_percent:.1f}%")
    else:
        lines.append("* None")
    
    lines.append("")
    
    # Healthy
    lines.append("### ✅ Healthy\n")
    if stable:
        fra_groups = [dg for dg in stable if dg.diskgroup_name == 'FRA']
        data_groups = [dg for dg in stable if dg.diskgroup_name != 'FRA']
        if fra_groups:
            pct_range = f"{min(dg.used_percent for dg in fra_groups):.0f}–{max(dg.used_percent for dg in fra_groups):.0f}%"
            lines.append(f"* FRA diskgroups mostly **low usage ({pct_range})**")
        if data_groups:
            for dg in data_groups:
                lines.append(f"* {dg.database} {dg.diskgroup_name} → ~{dg.used_percent:.0f}% (within limits)")
    
    lines.append("")
    
    # Observation
    lines.append("👉 **Observation:**\n")
    if critical:
        lines.append(f"* Main concern is **{critical[0].database} {critical[0].diskgroup_name} diskgroup (very high usage)**")
    lines.append("* Other environments are stable\n")
    
    return '\n'.join(lines)


def generate_mount_point_section(mount_points, section_title="PROD", section_num=3):
    """Generate a mount point section of the report."""
    if not mount_points:
        return f"## {section_num}. 💾 {section_title} Mount Point Status\n\n> No mount point data available.\n\n"
    
    critical, warning, stable = categorize_by_threshold(mount_points, critical=80, warning=65)
    
    lines = [f"## {section_num}. 💾 {section_title} Mount Point Status\n"]
    
    # High Usage
    lines.append("### 🔴 High Usage Filesystems\n")
    if critical:
        for mp in sorted(critical, key=lambda x: x.used_percent, reverse=True):
            lines.append(f"* `{mp.mount_point}` → **{mp.used_percent:.0f}% used**")
    else:
        lines.append("* None ✅")
    
    lines.append("")
    
    # Moderate
    lines.append("### 🟡 Moderate\n")
    if warning:
        for mp in sorted(warning, key=lambda x: x.used_percent, reverse=True):
            lines.append(f"* `{mp.mount_point}` → ~{mp.used_percent:.0f}%")
    else:
        lines.append("* None")
    
    lines.append("")
    
    # Healthy
    lines.append("### ✅ Healthy\n")
    if stable:
        mount_list = ', '.join(f'`{mp.mount_point}`' for mp in stable[:6])
        lines.append(f"* {mount_list} → low usage")
    
    lines.append("")
    
    # Observation
    lines.append("👉 **Observation:**\n")
    if critical:
        lines.append(f"* `{critical[0].mount_point}` filesystem needs monitoring")
    lines.append("* No filesystem is critically full yet\n")
    
    return '\n'.join(lines)


def generate_alerts_section(data):
    """Generate the key alerts section."""
    lines = ["# 🚨 Overall Key Alerts (Today)\n"]
    
    alerts = []
    
    # Critical diskgroups
    for dg in data.diskgroups:
        if dg.used_percent >= 90:
            alerts.append(f"* **{dg.database} {dg.diskgroup_name} diskgroup (~{dg.used_percent:.0f}%) → Critical**")
    
    # Critical tablespaces
    critical_ts = [ts for ts in data.tablespaces if ts.used_percent >= 90]
    if critical_ts:
        alerts.append("* **Tablespaces >90%**")
        for ts in critical_ts:
            alerts.append(f"  * {ts.tablespace_name} ({ts.database})")
    
    # High mount points
    for mp in data.mount_points:
        if mp.used_percent >= 80:
            alerts.append(f"* **`{mp.mount_point}` mount point (~{mp.used_percent:.0f}%) → Needs monitoring**")
    
    if not alerts:
        alerts.append("* ✅ No critical alerts today")
    
    lines.extend(alerts)
    lines.append("")
    return '\n'.join(lines)


def generate_health_summary(data):
    """Generate the final health summary."""
    lines = ["# ✅ Final Health Summary\n"]
    
    # Check DEV/TST
    dev_tst_critical = any(
        ts.used_percent >= 90 
        for ts in data.tablespaces 
        if 'DEV' in ts.database or 'TST' in ts.database
    )
    
    # Check PROD
    prod_critical = any(
        ts.used_percent >= 90 
        for ts in data.tablespaces 
        if 'PRD' in ts.database
    )
    
    prod_dg_critical = any(
        dg.used_percent >= 90 
        for dg in data.diskgroups 
        if 'PRD' in dg.database
    )
    
    if dev_tst_critical:
        lines.append("* ⚠️ DEV/TST → Issues detected")
    else:
        lines.append("* ✅ DEV/TST → Stable")
    
    if prod_critical or prod_dg_critical:
        lines.append("* ⚠️ PROD → Moderate risk areas exist")
    else:
        lines.append("* ✅ PROD → Healthy")
    
    # Find most critical item
    all_critical = []
    for ts in data.tablespaces:
        if ts.used_percent >= 90:
            all_critical.append(f"{ts.database} ({ts.tablespace_name})")
    for dg in data.diskgroups:
        if dg.used_percent >= 90:
            all_critical.append(f"{dg.database} storage")
    
    if all_critical:
        lines.append(f"* 🔴 Critical focus → **{', '.join(set(all_critical))}**")
    
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
