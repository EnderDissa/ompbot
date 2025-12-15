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