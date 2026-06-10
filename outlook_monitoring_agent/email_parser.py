"""
Email Parser Module
Parses monitoring email body content to extract:
- Tablespace utilization data
- Diskgroup (ASM) status
- Mount point usage
"""

import re
from dataclasses import dataclass, field


@dataclass
class TablespaceEntry:
    database: str
    tablespace_name: str
    used_percent: float
    size_mb: float = 0
    free_mb: float = 0


@dataclass
class DiskgroupEntry:
    database: str
    diskgroup_name: str
    used_percent: float
    total_gb: float = 0
    free_gb: float = 0


@dataclass
class MountPointEntry:
    host: str
    mount_point: str
    used_percent: float
    total_gb: float = 0
    available_gb: float = 0


@dataclass
class MonitoringData:
    tablespaces: list = field(default_factory=list)
    diskgroups: list = field(default_factory=list)
    mount_points: list = field(default_factory=list)
    source_subject: str = ""
    report_date: str = ""


# Database/instance section header, e.g. CTSPRD, CDBPRD, EBSPRD, HFAPRD,
# REPPRD, CTSTST, CTSDEV, CDBDEV, EBSTST, HFATST, etc.
DB_HEADER_RE = re.compile(
    r'^([A-Z]{2,4}(?:PRD|PROD|TST|TEST|DEV|QTS|QA)\d*)\s*$',
    re.IGNORECASE
)


def _unwrap_numeric_tails(lines):
    """
    Re-join lines that Outlook wrapped in the middle of a number.

    The plain-text email body wraps at ~79 chars, which can split a value
    such as ``88.3`` into ``88.`` + ``3`` or ``92`` into ``9`` + ``2``.
    A continuation line that is purely digits is glued back onto the
    previous line when that line ends with a digit or a dot.
    """
    out = []
    for raw in lines:
        s = raw.rstrip('\n')
        stripped = s.strip()
        if stripped and re.fullmatch(r'\d+', stripped) and out:
            prev = out[-1].rstrip()
            if re.search(r'[\d.]$', prev):
                out[-1] = prev + stripped
                continue
        out.append(s)
    return out


def parse_tablespace_data(email_body):
    """
    Parse tablespace monitoring data from email body.

    Expected format (DB name is a section header; %USED is the last column
    and may be wrapped across two lines by Outlook):

        CTSPRD
        ===1==
        TABLESPACE_NAME    MAXSIZE(GB) CURSIZE(GB) USED(GB) %USED OF MAX SIZE
        ------------------ ----------- ----------- -------- -------------------
        TS_ESONG_DATA               20          19       18                88.3
        TS_REPLICATION              16          16       15                  92
    """
    entries = []
    lines = _unwrap_numeric_tails(email_body.split('\n'))

    # NAME  MAX  CUR  USED  %USED   (name + 4 numeric columns)
    row_re = re.compile(
        r'^([A-Z][A-Z0-9_$#]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$',
        re.IGNORECASE
    )

    current_db = ""

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # Skip header / separator rows
        if line.upper().startswith('TABLESPACE_NAME') or set(line) <= set('-= '):
            continue

        # Labeled DB context (Database: X)
        db_header = re.match(r'(?:Database|DB|Instance)[:\s]+(\w+)', line, re.IGNORECASE)
        if db_header:
            current_db = db_header.group(1).upper()
            continue

        # Standalone DB section header (CTSPRD, CDBPRD, ...)
        db_section = DB_HEADER_RE.match(line)
        if db_section:
            current_db = db_section.group(1).upper()
            continue

        match = row_re.match(line)
        if match and current_db:
            entries.append(TablespaceEntry(
                database=current_db,
                tablespace_name=match.group(1).upper(),
                used_percent=float(match.group(5)),
                size_mb=float(match.group(2)),
                free_mb=float(match.group(2)) - float(match.group(4)),
            ))

    return entries



def parse_diskgroup_data(email_body):
    """
    Parse ASM diskgroup monitoring data from email body.

    Expected format (no '%' symbol; PCT_USED is the last column):

        CTSPRD
        ==1===
        GROUP_NAME    TOTAL_GB    FREE_GB    USED_GB   PCT_USED
        ----------    --------    -------    -------   --------
        DATA             24576        5212      19363      78.79
        BULK             15360        4440      10920       71.1
        FRA               8192        5473       2719      33.19
    """
    entries = []
    lines = email_body.split('\n')

    # Known ASM diskgroup names
    dg_names = r'DATA|FRA|REDO|ARCH|BULK|RECO'

    # Row with full columns: NAME TOTAL FREE USED PCT  (PCT may be like ".01")
    row_full = re.compile(
        rf'^({dg_names})\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$',
        re.IGNORECASE
    )
    # Fallback: NAME ... <last number is PCT>
    row_simple = re.compile(
        rf'^({dg_names})\b.*?([\d.]+)\s*%?\s*$', re.IGNORECASE
    )

    current_db = ""

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # Skip header/separator lines
        if line.upper().startswith('GROUP_NAME') or set(line) <= set('- '):
            continue

        # Detect DB context from labeled headers
        db_header = re.match(r'(?:Database|DB|Instance|Host)[:\s]+(\w+)', line, re.IGNORECASE)
        if db_header:
            current_db = db_header.group(1)
            continue

        # Detect DB context from a standalone instance header (e.g. CTSPRD, CDBPRD)
        db_section = DB_HEADER_RE.match(line)
        if db_section:
            current_db = db_section.group(1)
            continue

        # Full row with all columns
        match = row_full.match(line)
        if match:
            entries.append(DiskgroupEntry(
                database=current_db.upper(),
                diskgroup_name=match.group(1).upper(),
                used_percent=float(match.group(5)),
                total_gb=float(match.group(2)),
                free_gb=float(match.group(3)),
            ))
            continue

        # Simple fallback row
        match = row_simple.match(line)
        if match and current_db:
            entries.append(DiskgroupEntry(
                database=current_db.upper(),
                diskgroup_name=match.group(1).upper(),
                used_percent=float(match.group(2)),
            ))

    return entries


def parse_mount_point_data(email_body):
    """
    Parse mount point / filesystem usage data from a `df -h` style email.

    The database/host is a section header (e.g. CTSPRD, EBSPRD, CTSTST,
    CTSDEV, EBSTST). Each filesystem row ends with the "Mounted on" path,
    preceded by the integer Use%:

        CTSPRD
        ===1===
        Filesystem    Size  Used Avail Use% Mounted on
        /dev/xvda1     99G   34G   61G  37% /
        /dev/xvdf1     99G   76G   18G  82% /a01

    We anchor on ``<NN>% <mountpoint>`` so that Outlook line-wrapping and
    df's own device-name wrapping are both handled correctly.
    """
    entries = []
    lines = email_body.split('\n')

    # "<use%> <mounted-on path>"  e.g. "82% /a01", "1% /dev/shm"
    use_re = re.compile(r'(\d+)%\s+(/\S*)')

    current_host = ""

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # Labeled host context (Host: X)
        host_header = re.match(r'(?:Host|Server|Node)[:\s]+(\S+)', line, re.IGNORECASE)
        if host_header:
            current_host = host_header.group(1).upper()
            continue

        # Standalone DB/host section header (CTSPRD, EBSPRD, ...)
        db_section = DB_HEADER_RE.match(line)
        if db_section:
            current_host = db_section.group(1).upper()
            continue

        # Skip the df column header
        if line.lower().startswith('filesystem'):
            continue

        for m in use_re.finditer(raw):
            entries.append(MountPointEntry(
                host=current_host,
                mount_point=m.group(2),
                used_percent=float(m.group(1)),
            ))

    return entries


def classify_email(subject):
    """Classify email type based on subject line."""
    subject_lower = subject.lower()
    
    if 'tablespace' in subject_lower:
        return 'tablespace'
    elif 'diskgroup' in subject_lower or 'asm' in subject_lower:
        return 'diskgroup'
    elif 'mount' in subject_lower or 'filesystem' in subject_lower or 'disk' in subject_lower:
        return 'mount_point'
    elif 'monitoring' in subject_lower:
        return 'general'
    return 'unknown'


def parse_monitoring_emails(emails):
    """
    Parse a list of monitoring emails and return structured data.
    
    Args:
        emails: List of email dicts with 'subject', 'body', 'received_time'
    
    Returns:
        MonitoringData object with all parsed information
    """
    data = MonitoringData()
    
    for email in emails:
        subject = email['subject']
        body = email['body']
        email_type = classify_email(subject)
        
        if email_type == 'tablespace':
            data.tablespaces.extend(parse_tablespace_data(body))
        elif email_type == 'diskgroup':
            data.diskgroups.extend(parse_diskgroup_data(body))
        elif email_type == 'mount_point':
            data.mount_points.extend(parse_mount_point_data(body))
        elif email_type == 'general':
            # Try to parse all types
            data.tablespaces.extend(parse_tablespace_data(body))
            data.diskgroups.extend(parse_diskgroup_data(body))
            data.mount_points.extend(parse_mount_point_data(body))
        
        if not data.source_subject:
            data.source_subject = subject
        if not data.report_date and email.get('received_time'):
            data.report_date = str(email['received_time'].date())
    
    return data
