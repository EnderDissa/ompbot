# -*- coding: utf-8 -*-
import logging
import threading
import time
from datetime import datetime
from typing import Optional

from utils.mail_reciever import MailReceiver

logger = logging.getLogger(__name__)


class MailSyncWorker:
    def __init__(self, poll_interval: int = 300, min_confidence: int = 80):
        self.poll_interval = poll_interval
        self.min_confidence = min_confidence

        self.mail_receiver = MailReceiver()
        self.running = False
        self.thread: Optional[threading.Thread] = None

        self.last_reconciliation_count: int = 0
        self.last_check: Optional[str] = None
        self.last_error_count: int = 0

    def start(self):
        if self.running:
            logger.warning('MailSyncWorker already running')
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f'MailSyncWorker started (interval: {self.poll_interval}s)')

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.mail_receiver.disconnect()
        logger.info('MailSyncWorker stopped')

    def _run_loop(self):
        while self.running:
            try:
                self._sync_once()
            except Exception as e:
                logger.error(f'Error in MailSyncWorker: {e}')
                self.last_error_count += 1

            for _ in range(self.poll_interval):
                if not self.running:
                    break
                time.sleep(1)

    def _sync_once(self):
        logger.debug(f'Starting mail sync at {datetime.now().isoformat()}')

        if not self.mail_receiver.connect():
            logger.error('Failed to connect IMAP')
            return

        try:
            emails = self.mail_receiver.fetch_emails(days=7)
            for email_info in emails:
                self.mail_receiver.save_received_email(email_info)

            reconciled = self.mail_receiver.auto_reconcile(
                min_confidence=self.min_confidence
            )
            self.mail_receiver.export_reconciliation_report(reconciled)

            self.last_reconciliation_count = len(reconciled)
            self.last_check = datetime.now().isoformat()

            logger.info(f'Sync completed: {len(reconciled)} reconciled')

        finally:
            self.mail_receiver.disconnect()


class MailSyncManager:
    _instance: Optional['MailSyncManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.worker = None
        return cls._instance

    def start(self, poll_interval: int = 300):
        if self.worker is not None and self.worker.running:
            logger.warning('MailSyncManager already running')
            return

        self.worker = MailSyncWorker(poll_interval=poll_interval)
        self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()

    def force_sync(self) -> dict:
        if not self.worker:
            return {'status': 'error', 'message': 'Worker not initialized'}

        try:
            self.worker._sync_once()
            return {'status': 'success', 'message': 'Sync completed'}
        except Exception as e:
            logger.error(f'Error during force sync: {e}')
            return {'status': 'error', 'message': str(e)}

    def get_metrics(self) -> dict:
        if not self.worker:
            return {}

        try:
            sent = self.worker.mail_receiver.load_sent_docs()
            received = self.worker.mail_receiver.load_received_docs()

            return {
                'emails_received': len(received),
                'documents_sent': len(sent),
                'documents_reconciled': self.worker.last_reconciliation_count,
                'reconciliation_failed': self.worker.last_error_count,
                'last_check': self.worker.last_check or 'Never'
            }
        except Exception:
            return {}


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    manager = MailSyncManager()
    manager.start(poll_interval=60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Stopping...')
        manager.stop()