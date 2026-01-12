# -*- coding: utf-8 -*-
import hashlib
import imaplib
import json
import logging
from datetime import datetime, timedelta
from email.header import decode_header
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional, List, Dict

from utils import get_secrets

logger = logging.getLogger(__name__)


class MailReceiver:
    def __init__(self):
        self.our_addr = 'omp@itmo.ru'
        self.ufb_addr = 'dberman@itmo.ru'
        self.imap_server = 'imap.mail.ru'
        self.imap_port = 993
        self.imap = None

        secrets = get_secrets()
        self.mail_password = secrets.get('mail_password')

        self.sent_docs_file = 'data/sent_docs.json'
        self.received_docs_file = 'data/received_docs.json'
        self._init_storage()

    def _decode_mime_header(self, value) -> str:
        if isinstance(value, bytes):
            try:
                return value.decode('utf-8', errors='ignore')
            except Exception:
                return ''

        if isinstance(value, str):
            try:
                decoded_parts = decode_header(value)
                result = ""
                for part, encoding in decoded_parts:
                    if isinstance(part, bytes):
                        if encoding:
                            result += part.decode(encoding, errors='ignore')
                        else:
                            result += part.decode('utf-8', errors='ignore')
                    else:
                        result += str(part).strip()
                return result.strip()
            except Exception:
                return value

        return str(value)

    def _init_storage(self):
        Path('data').mkdir(exist_ok=True)

        for filepath in [self.sent_docs_file, self.received_docs_file]:
            p = Path(filepath)
            if not p.exists():
                with p.open('w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)

    def connect(self) -> bool:
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.imap.login(self.our_addr, self.mail_password)
            logger.info(f'Connected to IMAP: {self.imap_server}')
            return True
        except Exception as e:
            logger.error(f'Failed to connect IMAP: {e}')
            self.imap = None
            return False

    def disconnect(self):
        if self.imap:
            try:
                self.imap.close()
            except Exception:
                pass
            try:
                self.imap.logout()
            except Exception:
                pass
            self.imap = None

    def fetch_emails(self, days: int = 7) -> List[Dict]:
        if not self.imap:
            logger.error('IMAP not connected')
            return []

        try:
            ufb_folder = '&BCMEJAQR-'
            status, _ = self.imap.select(ufb_folder)
            if status != 'OK':
                logger.warning(f'Cannot select folder {ufb_folder}: {status}')
                return []

            since_date = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
            status, email_ids = self.imap.search(None, f'SINCE {since_date}')

            if status != 'OK':
                logger.warning(f'Email search failed: {status}')
                return []

            emails = []
            for email_id in email_ids[0].split():
                status, msg_data = self.imap.fetch(email_id, '(RFC822)')
                if status != 'OK' or not msg_data:
                    continue

                try:
                    import email
                    msg = email.message_from_bytes(msg_data[0][1])
                    email_info = self._parse_email(msg, email_id)
                    if email_info:
                        emails.append(email_info)
                except Exception as e:
                    logger.warning(f'Error parsing email: {e}')

            logger.info(f'Fetched {len(emails)} emails from folder')
            return emails

        except Exception as e:
            logger.error(f'Error fetching emails: {e}')
            return []

    def _parse_email(self, msg, email_id: bytes) -> Optional[Dict]:
        try:
            subject = self._decode_mime_header(msg.get('Subject', ''))
            sender = self._decode_mime_header(msg.get('From', ''))

            raw_date = msg.get('Date')
            if raw_date:
                try:
                    dt = parsedate_to_datetime(raw_date)
                    if dt.tzinfo:
                        dt = dt.astimezone().replace(tzinfo=None)
                    date_str = dt.isoformat()
                except Exception:
                    date_str = datetime.now().isoformat()
            else:
                date_str = datetime.now().isoformat()

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        try:
                            body = part.get_payload(decode=True).decode(
                                'utf-8', errors='ignore'
                            )
                        except Exception:
                            body = ""
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode(
                        'utf-8', errors='ignore'
                    )
                except Exception:
                    body = str(msg.get_payload())

            attachments = []
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_disposition() == 'attachment':
                        filename = part.get_filename()
                        if filename:
                            decoded_name = self._decode_mime_header(filename)
                            payload = part.get_payload(decode=True) or b""
                            attachments.append({
                                'filename': decoded_name,
                                'content_type': part.get_content_type(),
                                'size': len(payload)
                            })

            email_id_str = email_id.decode() if isinstance(email_id, bytes) else str(email_id)

            return {
                'id': email_id_str,
                'subject': subject,
                'sender': sender,
                'date': date_str,
                'body': body[:500],
                'attachments': attachments,
                'received_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f'Error parsing email: {e}')
            return None

    def save_received_email(self, email_info: Dict):
        try:
            with open(self.received_docs_file, 'r', encoding='utf-8') as f:
                docs = json.load(f)

            if email_info['id'] not in docs:
                docs[email_info['id']] = email_info

                with open(self.received_docs_file, 'w', encoding='utf-8') as f:
                    json.dump(docs, f, ensure_ascii=False, indent=2)

                logger.info(f'Saved email: {email_info["subject"]}')
            else:
                logger.debug(f'Email already exists: {email_info["id"]}')
        except Exception as e:
            logger.error(f'Error saving email: {e}')

    def load_sent_docs(self) -> Dict:
        try:
            with open(self.sent_docs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f'Error loading sent_docs: {e}')
            return {}

    def load_received_docs(self) -> Dict:
        try:
            with open(self.received_docs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f'Error loading received_docs: {e}')
            return {}

    def compare_documents(self, sent_doc: Dict, received_doc: Dict) -> Dict:
        matches = {
            'subject_match': False,
            'sender_match': False,
            'date_match': False,
            'status': 'NOT_MATCHED',
            'confidence': 0
        }

        # --- Critical safety guards ---
        # 1) Never reconcile on our own outgoing emails.
        #    This is the root cause of the "Автосогласование" false-positive:
        #    we send a message, it appears in the mailbox folder, and the bot
        #    mistakenly treats it as an approval.
        received_sender = (received_doc.get('sender', '') or '').lower()
        if self.our_addr.lower() in received_sender:
            # Self-sent email. Ignore completely.
            matches['status'] = 'SELF_SENT_IGNORED'
            matches['confidence'] = 0
            return matches

        # 2) Approval must come from trusted UFB addresses.
        #    Without this guard, any email with "СЗ" in subject can be matched.
        trusted_senders = {
            'pass@itmo.ru',
            'dberman@itmo.ru',
        }
        # Also allow configured ufb_addr if it differs.
        if self.ufb_addr:
            trusted_senders.add(self.ufb_addr.lower())

        if any(addr in received_sender for addr in trusted_senders):
            matches['sender_match'] = True
        else:
            # Sender mismatch => never reconcile.
            matches['confidence'] = 0
            matches['status'] = 'NOT_MATCHED'
            return matches

        sent_filename_raw = sent_doc.get('filename', '') or ''
        sent_filename = sent_filename_raw.lower()
        received_subject = (received_doc.get('subject', '') or '').lower()

        # --- Subject matching ---
        # We use the unique short-hash that is embedded into the outgoing email subject:
        #   "... ({unique})"
        # to avoid mixing different memos with the same club/token.
        unique = ''
        try:
            # Sent doc filename is expected like: "/СЗ_<club>_<document_name>.docx"
            # or similar. We reconstruct document_name the same way as in MailHelper.
            base = sent_filename.split('/')[-1]
            base = base.rsplit('.', 1)[0]
            parts = base.split('_', 2)
            # parts: ["сз", "<club>", "<document_name>"]
            document_name = parts[2] if len(parts) >= 3 else base
            # Keep the hashing logic local to avoid importing heavy modules.
            import hashlib
            hash_hex = hashlib.md5(document_name.encode('utf-8', errors='ignore')).hexdigest()
            unique = str(int(hash_hex, 16) % 1000000).zfill(6)
        except Exception:
            unique = ''

        subj_norm = received_subject.replace(' ', '_')
        subject_score = 0
        if unique and unique in received_subject:
            matches['subject_match'] = True
            subject_score = 60
        elif sent_filename:
            base = sent_filename.split('/')[-1]
            base = base.rsplit('.', 1)[0]
            parts = base.split('_')
            club_token = parts[1] if len(parts) >= 2 else ""

            base_norm = base.replace(' ', '_')
            club_norm = club_token.replace(' ', '_')

            # Strong match: full base name contained in subject
            if base_norm and base_norm in subj_norm:
                matches['subject_match'] = True
                subject_score = 60
            # Weaker match: club token only (still allowed but requires date match)
            elif club_norm and club_norm in subj_norm:
                matches['subject_match'] = True
                subject_score = 30

        try:
            sent_date_str = sent_doc.get('sent_at')
            received_date_str = received_doc.get('date')

            if sent_date_str and received_date_str:
                sent_date = datetime.fromisoformat(sent_date_str)
                received_date = datetime.fromisoformat(received_date_str)

                if received_date > sent_date and (received_date - sent_date).total_seconds() < 86400 * 7:
                    matches['date_match'] = True
        except Exception as e:
            logger.debug(f'Failed to parse dates for comparison: {e}')

        # Confidence model:
        # - Sender is mandatory (guard above). Still contributes.
        # - Subject is the primary matching signal.
        # - Date proximity helps disambiguate.
        confidence = (
            subject_score +
            (25 if matches['sender_match'] else 0) +
            (15 if matches['date_match'] else 0)
        )
        matches['confidence'] = confidence

        if confidence >= 80:
            matches['status'] = 'LIKELY_MATCH'
        elif confidence >= 60:
            matches['status'] = 'POSSIBLE_MATCH'
        else:
            matches['status'] = 'NOT_MATCHED'

        return matches

    def auto_reconcile(self, min_confidence: int = 70) -> List[Dict]:
        sent_docs = self.load_sent_docs()
        received_docs = self.load_received_docs()

        try:
            with open('data/reconciliation_report.json', 'r', encoding='utf-8') as f:
                existing_report = json.load(f)
                existing_reconciled = {item['sent_doc_id'] for item in existing_report.get('reconciled_docs', [])}
        except:
            existing_reconciled = set()

        reconciled = []

        logger.info(f'Comparing {len(sent_docs)} sent vs {len(received_docs)} received')

        for sent_id, sent_doc in sent_docs.items():
            if sent_id in existing_reconciled:
                logger.debug(f'Skipping already reconciled: {sent_id}')
                continue

            best_match = None
            best_confidence = 0

            for received_id, received_doc in received_docs.items():
                comparison = self.compare_documents(sent_doc, received_doc)
                if comparison['confidence'] > best_confidence:
                    best_confidence = comparison['confidence']
                    best_match = {
                        'sent_doc_id': sent_id,
                        'received_doc_id': received_id,
                        'comparison': comparison
                    }

            if best_match and best_confidence >= min_confidence:
                best_match['status'] = 'RECONCILED'
                reconciled.append(best_match)
                logger.info(
                    f'Reconciled: {sent_doc.get("filename", sent_id)} '
                    f'(confidence: {best_confidence}%)'
                )

        logger.info(f'Total reconciled: {len(reconciled)}')
        return reconciled

    def export_reconciliation_report(
        self,
        reconciled: List[Dict],
        output_file: str = 'data/reconciliation_report.json'
    ):
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'generated_at': datetime.now().isoformat(),
                    'reconciled_count': len(reconciled),
                    'reconciled_docs': reconciled
                }, f, ensure_ascii=False, indent=2)

            logger.info(f'Report saved: {output_file}')
        except Exception as e:
            logger.error(f'Error saving report: {e}')