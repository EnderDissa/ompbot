import imaplib
import json
import logging
from email.header import decode_header
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import hashlib
from pathlib import Path

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
            return value.decode('utf-8', errors='ignore')

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
            except:
                return value

        return str(value)
    def _init_storage(self):
        Path('data').mkdir(exist_ok=True)

        for filepath in [self.sent_docs_file, self.received_docs_file]:
            if not Path(filepath).exists():
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)

    def connect(self) -> bool:
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.imap.login(self.our_addr, self.mail_password)
            logger.info(f'Connected to IMAP: {self.imap_server}')
            return True
        except Exception as e:
            logger.error(f'Failed to connect IMAP: {e}')
            return False

    def disconnect(self):
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass

    def _decode_header(self, value) -> str:
        if isinstance(value, bytes):
            return value.decode('utf-8', errors='ignore')

        if isinstance(value, str):
            return value

        try:
            decoded_parts = decode_header(value)
            result = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    result += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    result += str(part)
            return result
        except:
            return str(value)

    def fetch_emails(self, days: int = 7) -> List[Dict]:
        if not self.imap:
            logger.error('IMAP not connected')
            return []

        try:
            ufb_folder = '&BCMEJAQR-'
            self.imap.select(ufb_folder)

            since_date = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
            status, email_ids = self.imap.search(None, f'SINCE {since_date}')

            if status != 'OK':
                logger.warning(f'Email search failed: {status}')
                return []

            emails = []
            for email_id in email_ids[0].split():
                status, msg_data = self.imap.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue

                try:
                    import email
                    msg = email.message_from_bytes(msg_data[0][1])
                    email_info = self._parse_email(msg, email_id)
                    if email_info:
                        emails.append(email_info)
                except Exception as e:
                    logger.warning(f'Error parsing email: {e}')

            logger.info(f'Fetched {len(emails)} emails from UFB folder')
            return emails

        except Exception as e:
            logger.error(f'Error fetching emails: {e}')
            return []

    def _parse_email(self, msg, email_id: bytes) -> Optional[Dict]:
        try:
            subject = self._decode_mime_header(msg.get('Subject', ''))
            sender = self._decode_mime_header(msg.get('From', ''))
            date_str = msg.get('Date', datetime.now().isoformat())

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    body = msg.get_payload()

            attachments = []
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_disposition() == 'attachment':
                        filename = part.get_filename()
                        if filename:
                            attachments.append({
                                'filename': self._decode_header(filename),
                                'content_type': part.get_content_type(),
                                'size': len(part.get_payload(decode=True))
                            })

            email_hash = hashlib.md5(
                f'{subject}|{sender}|{date_str}'.encode()
            ).hexdigest()[:16]

            return {
                'id': email_hash,
                'email_id': email_id.decode(),
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

            docs[email_info['id']] = email_info

            with open(self.received_docs_file, 'w', encoding='utf-8') as f:
                json.dump(docs, f, ensure_ascii=False, indent=2)

            logger.info(f'Saved email: {email_info["subject"]}')

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

        sent_filename = sent_doc.get('filename', '').lower()
        received_subject = received_doc.get('subject', '').lower()

        if 'auto' in sent_filename and 're:' in received_subject:
            matches['subject_match'] = True

        received_sender = received_doc.get('sender', '').lower()

        if 'pass@itmo.ru' in received_sender or 'dberman@itmo.ru' in received_sender:
            matches['sender_match'] = True

        try:
            sent_date = datetime.fromisoformat(sent_doc.get('sent_at', ''))
            received_date = datetime.fromisoformat(received_doc.get('date', ''))

            if received_date > sent_date and (received_date - sent_date).total_seconds() < 86400 * 7:
                matches['date_match'] = True
        except:
            pass

        confidence = sum([
            matches['subject_match'] * 40,
            matches['sender_match'] * 40,
            matches['date_match'] * 20
        ])
        matches['confidence'] = confidence

        if confidence >= 70:
            matches['status'] = 'LIKELY_MATCH'
        elif confidence >= 50:
            matches['status'] = 'POSSIBLE_MATCH'
        else:
            matches['status'] = 'NOT_MATCHED'

        return matches

    def auto_reconcile(self, min_confidence: int = 70) -> List[Dict]:
        sent_docs = self.load_sent_docs()
        received_docs = self.load_received_docs()
        reconciled = []

        logger.info(f'Comparing {len(sent_docs)} sent vs {len(received_docs)} received')

        for sent_id, sent_doc in sent_docs.items():
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
                    f'Reconciled: {sent_doc["filename"]} '
                    f'(confidence: {best_confidence}%)'
                )

        logger.info(f'Total reconciled: {len(reconciled)}')
        return reconciled

    def export_reconciliation_report(self, reconciled: List[Dict],
                                     output_file: str = 'data/reconciliation_report.json'):
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