# -*- coding: utf-8 -*-
import imaplib
import os
import smtplib
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from utils import get_secrets


class MailHelper:
    def __init__(self):
        self.our_addr = 'omp@itmo.ru'
        self.ufb_addr = '[Email11]'
        self.mail_password = get_secrets()["mail_password"]

    def send_mail(self, club_name: str, document_name: str, attachments):
        msg = MIMEMultipart()

        marker = f"AUTO-{int(time.time())}"
        short_marker = marker[-6:]

        msg['Subject'] = f"СЗ {club_name}: {document_name} ({short_marker})"
        msg['From'] = self.our_addr
        msg['To'] = self.ufb_addr

        body = f"""
        <p>Здравствуйте!</p>
        <p>Прошу согласовать служебную записку во вложении.</p>
        <p><strong>Клуб:</strong> {club_name}</p>
        <p><strong>Документ:</strong> {document_name}</p>
        <p><strong>Идентификатор:</strong> {marker}</p>
        <br>
        <blockquote>
        <img src="https://itmo.ru/file/pages/213/logo_osnovnoy_russkiy_chernyy.png" alt="ITMO" width="150"><br>
        <p>С уважением, [Surname5] [Name5] [Patronymic5]<br>
        Офис молодежных проектов | Youth Projects Office<br>
        <em>[Address8]<br>
        Email: omp@itmo.ru<br></em>
        <strong>Университет ИТМО | ITMO University <strong><br>
        <a href="https://itmo.ru/">itmo.ru</a>
        </p>
        </blockquote>
        """
        msg.attach(MIMEText(body, 'html', 'utf-8'))

        for attachment in attachments:
            if not os.path.isfile(attachment):
                continue
            with open(attachment, 'rb') as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment))
                part['Content-Disposition'] = (
                    f'attachment; filename="{os.path.basename(attachment)}"'
                )
                msg.attach(part)

        with smtplib.SMTP_SSL('smtp.mail.ru', 465) as mail:
            mail.login(self.our_addr, self.mail_password)
            mail.sendmail(self.our_addr, self.ufb_addr, msg.as_string())

        self.save_mail(msg)

    def save_mail(self, msg: MIMEMultipart):
        with imaplib.IMAP4_SSL('imap.mail.ru') as imap:
            imap.login(self.our_addr, self.mail_password)

            sent_folder = '&BCMEJAQR-'
            imap.select(sent_folder)

            imap.append(
                sent_folder,
                '',
                imaplib.Time2Internaldate(time.time()),
                msg.as_bytes()
            )

            try:
                if msg['Message-ID']:
                    status, data = imap.search(
                        None, 'HEADER', 'Message-ID', msg['Message-ID']
                    )
                    if status == 'OK':
                        email_ids = data[0].split()
                        for email_id in email_ids:
                            imap.store(email_id, '+FLAGS', '\\Seen')
            except Exception:
                pass

            imap.logout()