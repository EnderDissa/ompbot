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
        self.ufb_addr = 'dberman@itmo.ru'
        self.body = """
        
        <p>ЭТО ТЕСТ НОВОЙ ФИЧИ. ИГНОРИРУЙТЕ! Здравствуйте! Прошу согласовать служебную записку во вложении.</p>
        <br>
        
        <blockquote>
        <img src="https://itmo.ru/file/pages/213/logo_osnovnoy_russkiy_chernyy.png" alt="ITMO" width="150"><br>
        <p>С уважением, Берман Денис Константинович<br> 
        Офис молодежных проектов | Youth Projects Office<br>
        <em>Кронверкский пр., 49, лит. А, оф. 1111, Санкт-Петербург, Россия | Kronverksky Pr. 49, bldg. A, off. 1111, St. Petersburg, Russia<br>
        Email: omp@itmo.ru<br></em>
        <strong>Университет ИТМО | ITMO University <strong><br>
        <a href="https://itmo.ru/">itmo.ru</a>
        </p>
        </blockquote>
        """
        self.mail_password = get_secrets()["mail_password"]

    def send_mail(self, attachments):
        msg = MIMEMultipart()
        #Формируем сообщение
        msg['Subject'] = 'Согласование СЗ'
        msg['From'] = self.our_addr; msg['To'] = self.ufb_addr
        msg.attach(MIMEText(self.body, 'html'))

        for attachment in attachments:
            if not os.path.isfile(attachment):
                print(attachment)
                continue
            with open(attachment, 'rb') as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
                msg.attach(part)

        #Логинимся и отправляем
        with smtplib.SMTP_SSL('smtp.mail.ru', 465) as mail:
            mail.login('omp@itmo.ru', self.mail_password)
            mail.sendmail(self.our_addr, self.ufb_addr, msg.as_string())
        self.save_mail(msg)

    def save_mail(self, msg):
        with imaplib.IMAP4_SSL('imap.mail.ru') as imap:
            imap.login(self.our_addr, self.mail_password)

            #Отправка в нужную папку
            sent_folder = '&BCMEJAQR-'
            imap.select(sent_folder)
            imap.append(sent_folder, '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())

            #Сразу помечаем прочитанным
            status, data = imap.search(None, 'HEADER', 'Message-ID', msg['Message-ID'])
            email_ids = data[0].split()
            for email_id in email_ids:
                imap.store(email_id, '+FLAGS', '\\Seen')

            imap.logout()