import logging
import threading
import time
from typing import Optional

log = logging.getLogger(__name__)

class MailPoller:
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        protocol: str = "IMAP",
        poll_interval_sec: int = 15,
    ):
        self.host = host
        self.user = user
        self.password = password
        self.protocol = protocol.upper()
        self.poll_interval_sec = max(5, int(poll_interval_sec))

    def _poll_once(self) -> None:
        """
        Заглушка для будущей реализации.
        Тут будеn:
          - IMAP IDLE или
          - раз в N сек делаться SEARCH/UID SEARCH и обрабатываться новые письма
        Сейчас просто имитация.
        """
        log.debug("MailPoller: tick (host=%s, user=%s)", self.host, self.user)
        # TODO: заменить на реальную работу с почтой
        time.sleep(0.1)

    def run(self, stop_event: threading.Event) -> None:
        log.info("MailPoller: starting (interval=%ss)", self.poll_interval_sec)
        while not stop_event.is_set():
            try:
                self._poll_once()
            except Exception as e:
                log.exception("MailPoller error: %s", e)
                if stop_event.wait(3.0):
                    break
            if stop_event.wait(self.poll_interval_sec):
                break
        log.info("MailPoller: stopped")