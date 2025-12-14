import json
from datetime import datetime
from .mail_sync_worker import MailSyncManager


def save_sent_document(doc_id, filename, sender_uid, org):
    try:
        manager = MailSyncManager()
        if not manager.worker:
            return False

        sent_docs = manager.worker.mail_receiver.load_sent_docs()

        sent_docs[doc_id] = {
            'id': doc_id,
            'filename': filename,
            'sender_uid': sender_uid,
            'org': org,
            'sent_at': datetime.now().isoformat(),
            'status': 'sent'
        }

        with open('data/sent_docs.json', 'w', encoding='utf-8') as f:
            json.dump(sent_docs, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f'Error saving sent document: {e}')
        return False


def handle_admin_commands(msg, uid, admins):
    msg_lower = msg.lower()

    if msg_lower == '!sync' and uid in admins:
        manager = MailSyncManager()
        result = manager.force_sync()

        if result['status'] == 'success':
            return (uid, 'Mail sync completed')
        else:
            return (uid, f"Sync error: {result['message']}")

    if msg_lower == '!mail_stats' and uid in admins:
        manager = MailSyncManager()
        metrics = manager.get_metrics()

        message = (
            f"Sent documents: {metrics.get('sent_documents', 0)}\n"
            f"Received emails: {metrics.get('received_emails', 0)}\n"
            f"Last check: {metrics.get('last_check', 'Never')}"
        )
        return (uid, message)

    if msg_lower == '!mail_report' and uid in admins:
        try:
            with open('data/reconciliation_report.json', 'r', encoding='utf-8') as f:
                report = json.load(f)

            count = report.get('reconciled_count', 0)
            message = f'Reconciled documents: {count}'
            return (uid, message)
        except:
            return (uid, 'No reconciliation report found')

    return None
