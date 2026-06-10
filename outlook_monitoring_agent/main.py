"""
Friday Monitoring Summary Agent
================================
Reads monitoring emails from Outlook's "Friday Monitoring" folder,
parses tablespace/diskgroup/mount point data, and generates a 
formatted summary report.

Usage:
    python main.py                      # Auto-detect folder, use today's date
    python main.py --folder "Friday Monitoring"
    python main.py --date 2026-06-05
    python main.py --output report.md
    python main.py --list-folders       # List available Outlook folders
"""

import argparse
import re
import sys
import os
from datetime import datetime

from outlook_reader import (
    connect_outlook,
    get_folder,
    get_today_emails,
    get_friday_emails,
    get_emails_by_subject,
    send_email,
)
from email_parser import parse_monitoring_emails
from report_generator import generate_full_report, generate_html_report


# Your email address for receiving the summary report
RECIPIENT_EMAIL = "ajay.kumar@incedoinc.com"


# Email subject keywords to look for in the monitoring folder
MONITORING_KEYWORDS = [
    "tablespace",
    "diskgroup",
    "mount point",
    "monitoring",
    "disk",
    "ASM",
    "filesystem",
    "Thursday-Friday",
    "Friday",
]


def normalize_subject(subject):
    """Strip dates and extra whitespace so the same report type collapses to one key."""
    s = subject.lower()
    # Remove dates like "05-Jun-2026", "05 Jun 2026", "5-jun-26"
    s = re.sub(r'\d{1,2}[-/ ]*[a-z]{3,}[-/ ]*\d{2,4}', '', s)
    # Remove ISO dates like "2026-06-05"
    s = re.sub(r'\d{4}-\d{2}-\d{2}', '', s)
    # Collapse separators/whitespace
    s = re.sub(r'[-_]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def deduplicate_latest(emails):
    """
    Keep only the most recent email of each report type.

    Emails are expected to be sorted newest-first, so the first occurrence
    of each normalized subject is the latest one.
    """
    seen = set()
    unique = []
    for email in sorted(emails, key=lambda e: e['received_time'], reverse=True):
        key = normalize_subject(email['subject'])
        if key not in seen:
            seen.add(key)
            unique.append(email)
    return unique


def list_outlook_folders():
    """List all available Outlook folders for debugging."""
    print("Connecting to Outlook...")
    namespace = connect_outlook()
    
    print("\n📁 Available Outlook Folders:\n")
    inbox = namespace.GetDefaultFolder(6)
    print(f"  📨 {inbox.Name}")
    for folder in inbox.Folders:
        print(f"    └── {folder.Name} ({folder.Items.Count} items)")
        try:
            for subfolder in folder.Folders:
                print(f"        └── {subfolder.Name} ({subfolder.Items.Count} items)")
        except Exception:
            pass
    
    # Also check other top-level folders
    for store in namespace.Folders:
        print(f"\n  📦 {store.Name}")
        try:
            for folder in store.Folders:
                if folder.Name != inbox.Name:
                    print(f"    └── {folder.Name}")
        except Exception:
            pass


def run_agent(folder_name="Friday Monitoring", target_date=None, output_file=None, days_back=7, send_to=None):
    """
    Main agent workflow:
    1. Connect to Outlook
    2. Read emails from the monitoring folder
    3. Parse email content
    4. Generate summary report
    """
    print("=" * 60)
    print("  📊 Friday Monitoring Summary Agent")
    print("=" * 60)
    
    # Step 1: Connect to Outlook
    print("\n[1/4] Connecting to Outlook...")
    try:
        namespace = connect_outlook()
        print("  ✅ Connected successfully")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        print("\n  Make sure Outlook is running and accessible.")
        sys.exit(1)
    
    # Step 2: Get emails from the monitoring folder
    print(f"\n[2/4] Reading emails from '{folder_name}' folder...")
    try:
        folder = get_folder(namespace, folder_name)
        print(f"  ✅ Found folder: {folder.Name} ({folder.Items.Count} total items)")
    except FileNotFoundError as e:
        print(f"  ❌ {e}")
        print("\n  Use --list-folders to see available folders.")
        sys.exit(1)
    
    # Get emails based on date or keywords
    if target_date:
        emails = get_today_emails(folder, target_date)
        print(f"  📧 Found {len(emails)} emails for {target_date}")
    else:
        emails = get_emails_by_subject(folder, MONITORING_KEYWORDS, days_back)
        print(f"  📧 Found {len(emails)} monitoring emails (last {days_back} days)")
    
    if not emails:
        print("\n  ⚠️  No monitoring emails found!")
        print("  Tips:")
        print(f"    - Check if folder '{folder_name}' has recent emails")
        print("    - Try: python main.py --list-folders")
        print(f"    - Try increasing --days-back (current: {days_back})")
        sys.exit(0)
    
    # Keep only the latest email of each report type (drop older duplicates)
    total_found = len(emails)
    emails = deduplicate_latest(emails)
    print(f"  🧹 Using {len(emails)} latest email(s) after removing {total_found - len(emails)} duplicate(s)")
    
    # Show found emails
    print("\n  Found emails:")
    for i, email in enumerate(emails, 1):
        print(f"    {i}. [{email['received_time']}] {email['subject']}")
    
    # Step 3: Parse email content
    print(f"\n[3/4] Parsing monitoring data...")
    data = parse_monitoring_emails(emails)
    print(f"  ✅ Parsed:")
    print(f"    - {len(data.tablespaces)} tablespace entries")
    print(f"    - {len(data.diskgroups)} diskgroup entries")
    print(f"    - {len(data.mount_points)} mount point entries")
    
    # Step 4: Generate report
    print(f"\n[4/5] Generating summary report...")
    report_date = target_date.strftime('%d-%b-%Y') if target_date else datetime.now().strftime('%d-%b-%Y')
    day_name = datetime.now().strftime('%A')
    report = generate_full_report(data, report_date)
    html_report = generate_html_report(data, report_date)
    
    # Output - save to file
    if output_file:
        output_path = os.path.abspath(output_file)
    else:
        default_name = f"monitoring_summary_{datetime.now().strftime('%Y%m%d')}.md"
        output_path = os.path.join(os.path.dirname(__file__), default_name)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  ✅ Report saved to: {output_path}")
    
    # Send report via Outlook email
    recipient = send_to or RECIPIENT_EMAIL
    if recipient == "__skip__":
        print("\n  ⏭️  Skipping email (--no-email flag)")
    else:
        print(f"\n[5/5] Sending report to {recipient} via Outlook...")
        try:
            subject = f"📊 {day_name} Monitoring Summary ({report_date})"
            send_email(recipient, subject, report, body_html=html_report)
            print(f"  ✅ Email sent successfully to {recipient}")
        except Exception as e:
            print(f"  ❌ Failed to send email: {e}")
            print("  Report is still saved to file.")
    
    # Print report to console
    print("\n" + "=" * 60)
    print("  GENERATED REPORT")
    print("=" * 60 + "\n")
    print(report)
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Friday Monitoring Summary Agent - Reads Outlook emails and generates reports"
    )
    parser.add_argument(
        '--folder', '-f',
        default='Friday Monitoring',
        help='Outlook folder name to read from (default: "Friday Monitoring")'
    )
    parser.add_argument(
        '--date', '-d',
        type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
        help='Target date in YYYY-MM-DD format (default: auto-detect)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path for the report (default: auto-named .md file)'
    )
    parser.add_argument(
        '--days-back',
        type=int,
        default=7,
        help='Number of days to look back for emails (default: 7)'
    )
    parser.add_argument(
        '--list-folders',
        action='store_true',
        help='List all available Outlook folders and exit'
    )
    parser.add_argument(
        '--send-to', '-s',
        default=None,
        help='Email address to send the report to (default: ajay.kumar@incedoinc.com)'
    )
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Skip sending email, only save to file and print to console'
    )
    
    args = parser.parse_args()
    
    if args.list_folders:
        list_outlook_folders()
        return
    
    run_agent(
        folder_name=args.folder,
        target_date=args.date,
        output_file=args.output,
        days_back=args.days_back,
        send_to=args.send_to if not args.no_email else "__skip__",
    )


if __name__ == "__main__":
    main()
