"""
Outlook Email Reader Module
Connects to local Outlook application and reads emails from the Friday Monitoring folder.
"""

import win32com.client
from datetime import datetime, timedelta


def connect_outlook():
    """Connect to the local Outlook application."""
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        return namespace
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Outlook: {e}")


def get_folder(namespace, folder_name="Friday Monitoring", parent_folder="Inbox"):
    """
    Get emails from a specific Outlook folder.
    
    Args:
        namespace: Outlook MAPI namespace
        folder_name: Name of the subfolder to read from
        parent_folder: Parent folder (default: Inbox)
    
    Returns:
        Outlook folder object
    """
    try:
        inbox = namespace.GetDefaultFolder(6)  # 6 = Inbox
        
        # Try to find the subfolder
        for folder in inbox.Folders:
            if folder.Name.lower() == folder_name.lower():
                return folder
        
        # If not found in Inbox, search all folders
        for folder in namespace.Folders:
            try:
                for subfolder in folder.Folders:
                    if subfolder.Name.lower() == folder_name.lower():
                        return subfolder
                    for sub2 in subfolder.Folders:
                        if sub2.Name.lower() == folder_name.lower():
                            return sub2
            except Exception:
                continue
        
        raise FileNotFoundError(
            f"Folder '{folder_name}' not found. "
            f"Available Inbox subfolders: {[f.Name for f in inbox.Folders]}"
        )
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Error accessing folder: {e}")


def get_today_emails(folder, date=None):
    """
    Get emails from today (or a specific date) from the given folder.
    
    Args:
        folder: Outlook folder object
        date: Optional date to filter (defaults to today)
    
    Returns:
        List of email dictionaries with subject, body, received_time
    """
    if date is None:
        date = datetime.now().date()
    
    emails = []
    messages = folder.Items
    messages.Sort("[ReceivedTime]", True)  # Sort descending
    
    for msg in messages:
        try:
            received = msg.ReceivedTime.date()
            if received == date:
                emails.append({
                    "subject": msg.Subject,
                    "body": msg.Body,
                    "html_body": msg.HTMLBody if hasattr(msg, 'HTMLBody') else "",
                    "received_time": msg.ReceivedTime,
                    "sender": msg.SenderName,
                })
            elif received < date:
                break  # Since sorted descending, no more emails for this date
        except Exception:
            continue
    
    return emails


def get_friday_emails(folder):
    """Get emails from the most recent Friday (or today if it's Friday)."""
    today = datetime.now().date()
    days_since_friday = (today.weekday() - 4) % 7
    if days_since_friday == 0 and datetime.now().hour < 6:
        days_since_friday = 7
    last_friday = today - timedelta(days=days_since_friday)
    
    return get_today_emails(folder, last_friday)


def get_emails_by_subject(folder, subject_keywords, days_back=7):
    """
    Get emails matching subject keywords within the last N days.
    
    Args:
        folder: Outlook folder object
        subject_keywords: List of keywords to match in subject
        days_back: Number of days to look back
    
    Returns:
        List of matching email dictionaries
    """
    cutoff_date = (datetime.now() - timedelta(days=days_back)).date()
    emails = []
    messages = folder.Items
    messages.Sort("[ReceivedTime]", True)
    
    for msg in messages:
        try:
            received = msg.ReceivedTime.date()
            if received < cutoff_date:
                break
            
            subject_lower = msg.Subject.lower()
            if any(kw.lower() in subject_lower for kw in subject_keywords):
                emails.append({
                    "subject": msg.Subject,
                    "body": msg.Body,
                    "html_body": msg.HTMLBody if hasattr(msg, 'HTMLBody') else "",
                    "received_time": msg.ReceivedTime,
                    "sender": msg.SenderName,
                })
        except Exception:
            continue
    
    return emails


def send_email(to_address, subject, body_markdown, body_html=None):
    """
    Send an email via Outlook with the summary report.
    
    Args:
        to_address: Recipient email address
        subject: Email subject line
        body_markdown: Plain text / markdown body
        body_html: Optional HTML body (auto-generated from markdown if not provided)
    """
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)  # 0 = MailItem
        mail.To = to_address
        mail.Subject = subject
        
        if body_html:
            mail.HTMLBody = body_html
        else:
            # Convert markdown to basic HTML for Outlook rendering
            html_body = markdown_to_html(body_markdown)
            mail.HTMLBody = html_body
        
        mail.Body = body_markdown  # Plain text fallback
        mail.Send()
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to send email: {e}")


def markdown_to_html(md_text):
    """
    Convert markdown report to HTML for Outlook email display.
    Handles headers, bold, bullets, emojis, and code blocks.
    """
    import re
    
    lines = md_text.split('\n')
    html_lines = [
        '<html><body style="font-family: Calibri, Arial, sans-serif; font-size: 11pt; line-height: 1.5;">'
    ]
    
    in_list = False
    
    for line in lines:
        # Headers
        if line.startswith('# '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h1 style="color: #1a5276; border-bottom: 2px solid #2980b9; padding-bottom: 5px;">{line[2:]}</h1>')
        elif line.startswith('## '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h2 style="color: #2c3e50; margin-top: 20px;">{line[3:]}</h2>')
        elif line.startswith('### '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h3 style="color: #34495e;">{line[4:]}</h3>')
        elif line.startswith('* ') or line.startswith('  * '):
            if not in_list:
                html_lines.append('<ul style="margin: 5px 0;">')
                in_list = True
            indent = '&nbsp;&nbsp;&nbsp;&nbsp;' if line.startswith('  ') else ''
            content = line.lstrip(' *')
            # Bold
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
            # Code
            content = re.sub(r'`(.+?)`', r'<code style="background: #f0f0f0; padding: 2px 4px;">\1</code>', content)
            html_lines.append(f'<li>{indent}{content}</li>')
        elif line.startswith('👉'):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            html_lines.append(f'<p style="color: #d35400; margin-top: 10px;">{content}</p>')
        elif line.strip() == '':
            if in_list:
                html_lines.append('</ul>')
                in_list = False
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            content = re.sub(r'`(.+?)`', r'<code style="background: #f0f0f0; padding: 2px 4px;">\1</code>', content)
            html_lines.append(f'<p>{content}</p>')
    
    if in_list:
        html_lines.append('</ul>')
    
    html_lines.append('</body></html>')
    return '\n'.join(html_lines)
