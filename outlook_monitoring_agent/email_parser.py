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


def parse_tablespace_data(email_body):
    """
    Parse tablespace monitoring data from email body.
    Handles common formats:
    - DB_NAME | TABLESPACE_NAME | USED% | SIZE | FREE
    - Tabular or space-separated formats
    """
    entries = []
    lines = email_body.split('\n')
    
    # Patterns to match tablespace data
    # Pattern 1: DATABASE  TABLESPACE  USED_PCT
    pattern1 = re.compile(
        r'(\w+)\s+(\w+)\s+(\d+\.?\d*)\s*%', re.IGNORECASE
    )
    # Pattern 2: TABLESPACE_NAME  USED_PCT%  (with DB context from header)
    pattern2 = re.compile(
        r'(TS_\w+|SYSTEM|SYSAUX|USERS|UNDOTBS\d*|TEMP)\s+.*?(\d+\.?\d*)\s*%',
        re.IGNORECASE
    )
    # Pattern 3: Pipe-separated format
    pattern3 = re.compile(
        r'\|?\s*(\w+)\s*\|?\s*(TS_\w+|SYSTEM|SYSAUX|USERS|UNDOTBS\d*|TEMP)\s*\|?\s*(\d+\.?\d*)\s*%?',
        re.IGNORECASE
    )
    
    current_db = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect database context headers
        db_header = re.match(r'(?:Database|DB|Instance)[:\s]+(\w+)', line, re.IGNORECASE)
        if db_header:
            current_db = db_header.group(1)
            continue
        
        # Also detect DB name if it appears as a section header
        db_section = re.match(r'^(CDB\w+|CTS\w+|HFA\w+|GG\w+)\s*[:-]?\s*$', line, re.IGNORECASE)
        if db_section:
            current_db = db_section.group(1)
            continue
        
        # Try pattern 3 (pipe-separated) first
        match = pattern3.search(line)
        if match:
            db = match.group(1) if match.group(1) else current_db
            ts_name = match.group(2)
            pct = float(match.group(3))
            entries.append(TablespaceEntry(
                database=db.upper(),
                tablespace_name=ts_name.upper(),
                used_percent=pct
            ))
            continue
        
        # Try pattern 2
        match = pattern2.search(line)
        if match and current_db:
            ts_name = match.group(1)
            pct = float(match.group(2))
            entries.append(TablespaceEntry(
                database=current_db.upper(),
                tablespace_name=ts_name.upper(),
                used_percent=pct
            ))
            continue
    
    return entries


def parse_diskgroup_data(email_body):
    """Parse ASM diskgroup monitoring data from email body."""
    entries = []
    lines = email_body.split('\n')
    
    # Pattern: DISKGROUP_NAME  TOTAL  FREE  USED_PCT
    pattern = re.compile(
        r'(DATA|FRA|REDO|ARCH)\s+.*?(\d+\.?\d*)\s*%', re.IGNORECASE
    )
    # Pattern with DB context
    pattern_full = re.compile(
        r'(\w+)\s+(DATA|FRA|REDO|ARCH)\s+.*?(\d+\.?\d*)\s*%', re.IGNORECASE
    )
    
    current_db = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect DB context
        db_header = re.match(r'(?:Database|DB|Instance|Host)[:\s]+(\w+)', line, re.IGNORECASE)
        if db_header:
            current_db = db_header.group(1)
            continue
        
        db_section = re.match(r'^(CDB\w+|CTS\w+|HFA\w+|GG\w+)\s*[:-]?\s*$', line, re.IGNORECASE)
        if db_section:
            current_db = db_section.group(1)
            continue
        
        # Try full pattern
        match = pattern_full.search(line)
        if match:
            entries.append(DiskgroupEntry(
                database=match.group(1).upper(),
                diskgroup_name=match.group(2).upper(),
                used_percent=float(match.group(3))
            ))
            continue
        
        # Try simple pattern
        match = pattern.search(line)
        if match and current_db:
            entries.append(DiskgroupEntry(
                database=current_db.upper(),
                diskgroup_name=match.group(1).upper(),
                used_percent=float(match.group(2))
            ))
    
    return entries


def parse_mount_point_data(email_body):
    """Parse mount point / filesystem usage data from email body."""
    entries = []
    lines = email_body.split('\n')
    
    # Pattern: /mount/point  SIZE  USED  AVAIL  USE%
    pattern = re.compile(
        r'(/\S*)\s+\S+\s+\S+\s+\S+\s+(\d+)%', re.IGNORECASE
    )
    # Alternative: /mount  USED%
    pattern_alt = re.compile(
        r'(/\S+)\s+.*?(\d+)\s*%', re.IGNORECASE
    )
    
    current_host = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect host context
        host_header = re.match(r'(?:Host|Server|Node)[:\s]+(\S+)', line, re.IGNORECASE)
        if host_header:
            current_host = host_header.group(1)
            continue
        
        # Try standard df-like format
        match = pattern.search(line)
        if match:
            entries.append(MountPointEntry(
                host=current_host,
                mount_point=match.group(1),
                used_percent=float(match.group(2))
            ))
            continue
        
        # Try alternative format
        match = pattern_alt.search(line)
        if match and match.group(1).startswith('/'):
            entries.append(MountPointEntry(
                host=current_host,
                mount_point=match.group(1),
                used_percent=float(match.group(2))
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
