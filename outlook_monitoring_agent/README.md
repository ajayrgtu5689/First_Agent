# 📊 Friday Monitoring Summary Agent

Automatically reads monitoring emails from your Outlook "Friday Monitoring" folder and generates a formatted summary report with tablespace, diskgroup, and mount point status.

---

## 🛠️ Setup Steps

### Step 1: Prerequisites

- **Windows OS** with Microsoft Outlook desktop app installed and configured
- **Python 3.8+** installed
- Outlook must be **running** when you execute the agent

### Step 2: Install Dependencies

```powershell
cd outlook_monitoring_agent
pip install -r requirements.txt
```

This installs:
- `pywin32` — Windows COM interface to connect to Outlook
- `beautifulsoup4` — HTML email parsing
- `html2text` — Convert HTML emails to text

### Step 3: Create the Outlook Folder

1. Open **Outlook**
2. Right-click on **Inbox** → **New Folder**
3. Name it: `Friday Monitoring`
4. Create an Outlook **Rule** to auto-move monitoring emails to this folder:
   - Go to **Home** → **Rules** → **Manage Rules & Alerts**
   - Click **New Rule** → "Apply rule on messages I receive"
   - Condition: **with specific words in the subject**
     - Add: `tablespace`, `diskgroup`, `mount point`, `monitoring`
   - Action: **move it to the specified folder** → select "Friday Monitoring"
   - Click **Finish**

### Step 4: Run the Agent

```powershell
# Basic usage (reads from "Friday Monitoring" folder)
python main.py

# Specify a different folder
python main.py --folder "DBA Monitoring"

# Filter by specific date
python main.py --date 2026-06-05

# Save to a specific file
python main.py --output "C:\Reports\friday_report.md"

# List available Outlook folders (for troubleshooting)
python main.py --list-folders

# Look back more days
python main.py --days-back 14
```

---

## 📁 Project Structure

```
outlook_monitoring_agent/
├── main.py              # Main entry point / agent orchestrator
├── outlook_reader.py    # Outlook connection and email fetching
├── email_parser.py      # Parses email body into structured data
├── report_generator.py  # Generates formatted markdown report
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 📋 How It Works

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐     ┌─────────────────┐
│   Outlook   │────▶│ outlook_reader│────▶│  email_parser  │────▶│report_generator │
│  (Emails)   │     │  (Fetch)     │     │  (Parse Data)  │     │ (Format Report) │
└─────────────┘     └──────────────┘     └────────────────┘     └─────────────────┘
                                                                         │
                                                                         ▼
                                                                  📄 Summary Report
                                                                    (Markdown)
```

1. **Connect** to local Outlook via Windows COM
2. **Fetch** emails from the "Friday Monitoring" folder (filtered by date/keywords)
3. **Parse** email body to extract:
   - Tablespace utilization (database, tablespace name, % used)
   - ASM Diskgroup status (diskgroup name, % used)
   - Mount point/filesystem usage (path, % used)
4. **Categorize** entries by severity:
   - 🔴 Critical (≥90% for tablespaces, ≥90% for diskgroups, ≥80% for mounts)
   - 🟡 Warning (85-90% for tablespaces, 70-90% for diskgroups, 65-80% for mounts)
   - ✅ Stable (below thresholds)
5. **Generate** a formatted markdown report with all sections

---

## 🔧 Customization

### Change Thresholds

Edit `report_generator.py` → `categorize_by_threshold()` calls:
- Tablespace: `critical=90, warning=85`
- Diskgroup: `critical=90, warning=70`
- Mount points: `critical=80, warning=65`

### Add New Email Keywords

Edit `main.py` → `MONITORING_KEYWORDS` list to match your email subjects.

### Adjust Parsing Patterns

Edit `email_parser.py` if your monitoring emails have a different format.
The parser handles:
- Pipe-separated tables (`|`)
- Space-separated columns
- Percentage values with `%` symbol
- Database/host context headers

---

## 🚀 Automation (Optional)

### Schedule with Windows Task Scheduler

1. Open **Task Scheduler**
2. Create Basic Task → "Friday Monitoring Report"
3. Trigger: **Weekly** → Friday at 10:00 AM
4. Action: **Start a program**
   - Program: `python`
   - Arguments: `main.py --output "C:\Reports\friday_report.md"`
   - Start in: `<path_to_this_folder>`

### Schedule with PowerShell

```powershell
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "main.py --output C:\Reports\friday_report.md" `
    -WorkingDirectory "C:\path\to\outlook_monitoring_agent"

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At 10am

Register-ScheduledTask -TaskName "FridayMonitoringReport" `
    -Action $action -Trigger $trigger -Description "Generate Friday monitoring summary"
```

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Failed to connect to Outlook" | Make sure Outlook desktop app is running |
| "Folder not found" | Run `python main.py --list-folders` to see available folders |
| No emails found | Check `--days-back` value or verify emails are in the correct folder |
| Parsing issues | Check email format — the parser expects tabular data with % values |
| Permission error | Run as the same Windows user that owns the Outlook profile |
