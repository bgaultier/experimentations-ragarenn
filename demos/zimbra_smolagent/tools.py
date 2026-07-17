"""
Outils IMAP et CalDAV autonomes pour la manipulation agentique (Zimbra).
Les identifiants sont injectés par session (pas de var globale).
"""

import os
import imaplib
import email
import email.header
import email.utils
from email.mime.text import MIMEText
import time
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import uuid

import caldav
from icalendar import Calendar, Event, Todo, vCalAddress, vText, vRecur
from smolagents import Tool

# ── Identifiants par session ──────────────────────────────────────────────────

@dataclass
class ImapCredentials:
    server: str
    username: str
    password: str

# ── Classe de base : tool lié à une session ───────────────────────────────────

class _SessionTool(Tool):
    """Tool de base : reçoit les identifiants de la session."""
    def __init__(self, creds: ImapCredentials):
        super().__init__()
        self.creds = creds

# ==============================================================================
# ── IMAP TOOLS (Conservés à l'identique, encapsulation Tool) ──────────────────
# ==============================================================================

def get_imap_connection(creds: ImapCredentials) -> imaplib.IMAP4_SSL:
    if not all([creds.server, creds.username, creds.password]):
        raise ValueError("Identifiants IMAP incomplets.")
    try:
        mail = imaplib.IMAP4_SSL(creds.server, 993)
        mail.login(creds.username, creds.password)
        return mail
    except Exception as e:
        raise Exception(f"Échec de connexion IMAP à {creds.server} : {e}")

def _decode_header_value(value: str) -> str:
    decoded_parts = email.header.decode_header(value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            try: result.append(part.decode(charset or "utf-8", errors="replace"))
            except Exception: result.append(part.decode("utf-8", errors="replace"))
        else:
            result.append(str(part))
    return " ".join(result)

class ListEmailsTool(_SessionTool):
    name = "list_emails"
    description = "Liste les emails récents d'un dossier IMAP (défaut : INBOX)."
    inputs = {
        "limit":  {"type": "integer", "nullable": True, "description": "Nombre d'emails (défaut : 10)."},
        "folder": {"type": "string", "nullable": True, "description": "Nom du dossier IMAP (défaut : INBOX)."},
    }
    output_type = "string"

    def forward(self, limit: Optional[int] = 10, folder: str = "INBOX") -> str:
        mail = None
        try:
            mail = get_imap_connection(self.creds)
            mail.select(folder)
            status, data = mail.search(None, "ALL")
            all_ids = data[0].split()
            ids_to_fetch = all_ids[-limit:] if len(all_ids) > limit else all_ids
            
            emails = []
            for num in ids_to_fetch:
                _, msg_data = mail.fetch(num, "(BODY.PEEK[HEADER])")
                msg = email.message_from_bytes(msg_data[0][1])
                emails.append({
                    "id": num.decode().strip(),
                    "date": msg.get("Date", "inconnue"),
                    "from": _decode_header_value(msg.get("From", "")),
                    "subject": _decode_header_value(msg.get("Subject", "(sans objet)")),
                })
        finally:
            if mail:
                try: mail.logout()
                except Exception: pass

        if not emails: return f"❌ Aucun email trouvé dans '{folder}'."
        lines = [f"=== {len(emails)} email(s) dans {folder} ==="]
        for e in reversed(emails):
            lines += [f"  [{e['id']}] {e['date']}", f"       De : {e['from']}", f"       Sujet : {e['subject']}", ""]
        return "\n".join(lines)

class GetEmailTool(_SessionTool):
    name = "get_email_content"
    description = "Récupère le contenu complet d'un email (en-têtes + corps text/plain)."
    inputs = {
        "email_id": {"type": "string", "description": "Identifiant IMAP du message."},
        "folder":   {"type": "string", "nullable": True, "description": "Dossier contenant le message (défaut : INBOX)."},
    }
    output_type = "string"

    def forward(self, email_id: str, folder: str = "INBOX") -> str:
        mail = None
        try:
            mail = get_imap_connection(self.creds)
            mail.select(folder)
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")
                        break
            else:
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="replace")
        finally:
            if mail:
                try: mail.logout()
                except Exception: pass
        return f"=== Contenu du message ===\n{body}\n=== Fin du message ==="

class SearchEmailsTool(_SessionTool):
    name = "search_emails"
    description = (
        "Recherche des emails selon des critères optionnels : expéditeur, "
        "sujet, date. Les critères sont combinés en ET logique."
    )
    inputs = {
        "from_address": {"type": "string", "nullable": True,
                         "description": "Filtrer par expéditeur."},
        "subject":      {"type": "string", "nullable": True,
                         "description": "Filtrer par sujet."},
        "since":        {"type": "string", "nullable": True,
                         "description": "Filtrer par date (format IMAP : '01-Jan-2026')."},
        "folder":       {"type": "string", "nullable": True,
                         "description": "Dossier à parcourir (défaut : INBOX)."},
        "limit":        {"type": "integer", "nullable": True,
                         "description": "Nombre max de résultats (défaut : 10)."},
    }
    output_type = "string"

    def forward(self, from_address: Optional[str] = None, subject: Optional[str] = None, 
                since: Optional[str] = None, folder: str = "INBOX", limit: Optional[int] = 10) -> str:
        mail = None
        try:
            mail = get_imap_connection(self.creds)
            status, _ = mail.select(folder)
            if status != "OK":
                return f"❌ Impossible d'ouvrir le dossier '{folder}'."

            criteria = []
            if from_address: criteria.append(f'FROM "{from_address}"')
            if subject: criteria.append(f'SUBJECT "{subject}"')
            if since: criteria.append(f'SINCE "{since}"')
            search_criteria = " ".join(criteria) if criteria else "ALL"

            status, data = mail.search(None, search_criteria)
            if status != "OK" or not data[0]:
                return "❌ Aucun email trouvé avec ces critères."

            all_ids = data[0].split()
            ids_to_fetch = all_ids[-limit:] if len(all_ids) > limit else all_ids

            emails = []
            for num in ids_to_fetch:
                _, msg_data = mail.fetch(num, "(BODY.PEEK[HEADER])")
                msg = email.message_from_bytes(msg_data[0][1])
                emails.append({
                    "id": num.decode().strip(),
                    "date": msg.get("Date", "inconnue"),
                    "from": _decode_header_value(msg.get("From", "")),
                    "subject": _decode_header_value(msg.get("Subject", "(sans objet)")),
                })
        finally:
            if mail:
                try: mail.logout()
                except Exception: pass

        if not emails:
            return "❌ Aucun email trouvé avec ces critères."

        lines = [f"=== {len(emails)} résultat(s) dans {folder} ==="]
        for e in reversed(emails):
            lines += [f"  [{e['id']}] {e['date']}",
                      f"       De : {e['from']}",
                      f"       Sujet : {e['subject']}", ""]
        return "\n".join(lines)


class CreateDraftTool(_SessionTool):
    name = "create_draft"
    description = (
        "Crée un brouillon d'email dans le dossier Drafts. "
        "Nécessite le destinataire (to), l'objet (subject) et le corps (body)."
    )
    inputs = {
        "to":      {"type": "string", "description": "Adresse du destinataire."},
        "subject": {"type": "string", "description": "Objet du message."},
        "body":    {"type": "string", "description": "Corps du message (texte brut)."},
    }
    output_type = "string"

    def forward(self, to: str, subject: str, body: str) -> str:
        mail = None
        try:
            mail = get_imap_connection(self.creds)
            
            # Création du message MIME
            msg = MIMEText(body, "plain", "utf-8")
            msg["From"] = self.creds.username
            msg["To"] = to
            msg["Subject"] = email.header.Header(subject, "utf-8")
            msg["Date"] = email.utils.formatdate(localtime=True)
            
            # Ajout au dossier Drafts
            mail.append("Drafts", "\\Draft",
                        imaplib.Time2Internaldate(time.time()), msg.as_bytes())
            
            success = True
        except Exception as e:
            return f"❌ Échec de la création du brouillon : {e}"
        finally:
            if mail:
                try: mail.logout()
                except Exception: pass

        return (f"✅ Brouillon créé dans Drafts :\n"
                f"   Destinataire : {to}\n"
                f"   Objet        : {subject}\n"
                f"   Longueur     : {len(body)} caractères")

# ==============================================================================
# ── CALDAV TOOLS (Adaptés pour utiliser la session) ───────────────────────────
# ==============================================================================

def get_caldav_client(creds: ImapCredentials) -> caldav.DAVClient:
    url = os.getenv("CALDAV_URL", "https://z.imt.fr/")
    return caldav.DAVClient(url=url, username=creds.username, password=creds.password)

def ensure_local_tz(dt_str: str) -> datetime:
    dt = datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return dt

class GetCurrentTimeTool(Tool):
    name = "get_current_time"
    description = "Get the current local system time to calculate relative dates."
    inputs = {}
    output_type = "string"
    
    def forward(self) -> str:
        now = datetime.now().astimezone()
        return f"Current Date: {now.strftime('%A, %B %d, %Y')}\nISO format: {now.isoformat()}"

class ListCalendarsTool(_SessionTool):
    name = "list_calendars"
    description = "Lists all available calendars and task lists on the CalDAV server."
    inputs = {}
    output_type = "string"

    def forward(self) -> str:
        client = get_caldav_client(self.creds)
        calendars = client.principal().calendars()
        res = [f"- {cal.name or 'Unknown'} (URL: {cal.url})" for cal in calendars]
        return "Calendars found:\n" + "\n".join(res)

class CreateEventTool(_SessionTool):
    name = "create_event"
    description = "Creates a new calendar event, with support for recurrence (rrule) and attendees."
    inputs = {
        "calendar_name": {"type": "string", "description": "Display name of the calendar."},
        "summary": {"type": "string", "description": "Title of the event."},
        "start_time": {"type": "string", "description": "ISO 8601 24h format (e.g., '2026-07-16T14:30:00')."},
        "end_time": {"type": "string", "description": "ISO 8601 24h format."},
        "rrule": {"type": "string", "nullable": True, "description": "Recurrence rule (e.g. 'FREQ=WEEKLY;COUNT=5')."},
        "description": {"type": "string", "nullable": True, "description": "Details about the event."}
    }
    output_type = "string"

    def forward(self, calendar_name: str, summary: str, start_time: str, end_time: str, rrule: str = "", description: str = "") -> str:
        client = get_caldav_client(self.creds)
        target_cal = next((c for c in client.principal().calendars() if c.name == calendar_name), None)
        if not target_cal: return f"Error: Calendar '{calendar_name}' not found."

        dt_start = ensure_local_tz(start_time)
        dt_end = ensure_local_tz(end_time)

        cal = Calendar()
        cal.add('prodid', '-//smolagents CalDAV Assistant//')
        cal.add('version', '2.0')

        event = Event()
        event.add('summary', summary)
        event.add('dtstart', dt_start)
        event.add('dtend', dt_end)
        event.add('dtstamp', datetime.now().astimezone())
        
        if description: event.add('description', description)
        if rrule: event.add('rrule', vRecur.from_ical(rrule))

        cal.add_component(event)
        target_cal.save_event(ical=cal.to_ical())
        return f"✅ Event created: '{summary}' on {dt_start.strftime('%Y-%m-%d %H:%M')}"

class GetEventsTool(_SessionTool):
    name = "get_events"
    description = "Get events within a time range. Expands recurring events automatically."
    inputs = {
        "calendar_name": {"type": "string", "description": "Display name of the calendar."},
        "start_time": {"type": "string", "description": "ISO 8601 string for search start."},
        "end_time": {"type": "string", "description": "ISO 8601 string for search end."}
    }
    output_type = "string"

    def forward(self, calendar_name: str, start_time: str, end_time: str) -> str:
        client = get_caldav_client(self.creds)
        target_cal = next((c for c in client.principal().calendars() if c.name == calendar_name), None)
        if not target_cal: return f"Error: Calendar '{calendar_name}' not found."

        dt_start = ensure_local_tz(start_time)
        dt_end = ensure_local_tz(end_time)

        results = target_cal.date_search(start=dt_start, end=dt_end, expand=True)
        events = []
        for event in results:
            event.load()
            for component in event.icalendar_component.walk():
                if component.name == "VEVENT":
                    s = component.get('dtstart')
                    events.append(f"- {component.get('summary')} (Start: {s.dt.isoformat() if hasattr(s, 'dt') else s})")
        
        return "\n".join(events) if events else "No events found in this timeframe."
    
# ==============================================================================
# ── CALDAV TOOLS : TÂCHES (VTODO) ─────────────────────────────────────────────
# ==============================================================================

class CreateTaskTool(_SessionTool):
    name = "create_task"
    description = (
        "Crée une nouvelle tâche (VTODO) dans un calendrier Zimbra spécifique. "
        "Permet de définir une date d'échéance (due date)."
    )
    inputs = {
        "calendar_name": {"type": "string", "description": "Nom du calendrier/liste de tâches (ex: 'Tasks' ou 'Tâches')."},
        "summary":       {"type": "string", "description": "Titre ou résumé de la tâche."},
        "due_date":      {"type": "string", "nullable": True, "description": "Date limite au format ISO 8601 (ex: '2026-07-20T18:00:00'). Optionnel."},
        "status":        {"type": "string", "nullable": True, "description": "Statut de la tâche : 'NEEDS-ACTION', 'IN-PROCESS', 'COMPLETED', 'CANCELLED'. Défaut: 'NEEDS-ACTION'."}
    }
    output_type = "string"

    def forward(self, calendar_name: str, summary: str, due_date: Optional[str] = None, status: Optional[str] = "NEEDS-ACTION") -> str:
        client = get_caldav_client(self.creds)
        try:
            principal = client.principal()
            calendars = principal.calendars()
            
            target_cal = next((c for c in calendars if c.name == calendar_name), None)
            if not target_cal:
                return f"❌ Calendrier ou liste de tâches '{calendar_name}' introuvable."

            # Création du conteneur VCALENDAR
            cal = Calendar()
            cal.add('prodid', '-//smolagents CalDAV Task Tool//FR')
            cal.add('version', '2.0')

            # Création du composant VTODO
            todo = Todo()
            todo.add('uid', str(uuid.uuid4()))
            todo.add('summary', vText(summary))
            todo.add('status', vText(status.upper() if status else "NEEDS-ACTION"))
            
            # Ajout des dates
            now = datetime.now().astimezone()
            todo.add('dtstamp', now)
            
            if due_date:
                todo.add('due', ensure_local_tz(due_date))

            cal.add_component(todo)
            ics_data = cal.to_ical().decode("utf-8")

            # Sauvegarde sur le serveur
            target_cal.save_todo(ics_data)
            
            return f"✅ Tâche '{summary}' créée avec succès dans '{calendar_name}'."
            
        except Exception as e:
            return f"❌ Erreur lors de la création de la tâche : {str(e)}"

class GetTasksTool(_SessionTool):
    name = "get_tasks"
    description = (
        "Récupère les tâches (VTODO) d'un calendrier/liste spécifique. "
        "Peut filtrer pour n'afficher que les tâches en cours."
    )
    inputs = {
        "calendar_name":  {"type": "string", "description": "Nom du calendrier/liste de tâches."},
        "pending_only":   {"type": "boolean", "nullable": True, "description": "Si True, exclut les tâches 'COMPLETED' ou 'CANCELLED'. Défaut : True."}
    }
    output_type = "string"

    def forward(self, calendar_name: str, pending_only: Optional[bool] = True) -> str:
        client = get_caldav_client(self.creds)
        try:
            principal = client.principal()
            calendars = principal.calendars()
            
            target_cal = next((c for c in calendars if c.name == calendar_name), None)
            if not target_cal:
                return f"❌ Calendrier ou liste de tâches '{calendar_name}' introuvable."

            # Récupération des todos (spécifique à CalDAV)
            todos = target_cal.todos()
            
            if not todos:
                return f"ℹ️ Aucune tâche trouvée dans '{calendar_name}'."

            tasks_data = []
            for t in todos:
                # Analyse du composant VTODO
                ical_obj = Calendar.from_ical(t.data)
                for component in ical_obj.walk():
                    if component.name == "VTODO":
                        summary = str(component.get('summary', 'Sans titre'))
                        status = str(component.get('status', 'NEEDS-ACTION')).upper()
                        
                        # Filtrage
                        if pending_only and status in ['COMPLETED', 'CANCELLED']:
                            continue
                            
                        due = component.get('due')
                        due_str = due.dt.strftime("%Y-%m-%d %H:%M") if due else "Pas d'échéance"
                        
                        tasks_data.append(f"  - [{status}] {summary} (Échéance : {due_str})")

            if not tasks_data:
                return f"ℹ️ Aucune tâche correspondant aux critères dans '{calendar_name}'."

            lines = [f"=== Tâches de '{calendar_name}' ==="] + tasks_data
            return "\n".join(lines)
            
        except Exception as e:
            return f"❌ Erreur lors de la récupération des tâches : {str(e)}"