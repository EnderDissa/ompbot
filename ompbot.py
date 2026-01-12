# -*- coding: utf-8 -*-
import json
import uuid
import requests
from datetime import datetime as date
import re
import os
import shutil
from typing import Optional, Dict, Any

from utils import check_excel, create_excel, net_helper, mail_helper
from utils.mail_helper import MailHelper
from utils.mail_sync_worker import MailSyncManager
from utils.metrics import Metrics
from utils.user_list import UserList
from utils.mail_integration_helpers import save_sent_document
from utils.log import log

admin_chat = 1
admins = [297002785, 101822925]
groupid = 228288169


CLUB_NAME_RE = r'СЗ_[а-яёА-ЯЁa-zA-Z0-9_-]+\.'


def _extract_first_doc_attachment(attachments) -> Optional[Dict[str, Any]]:
    """Return VK 'doc' dict from attachments list, or None."""
    if not attachments:
        return None
    for a in attachments:
        if isinstance(a, dict) and a.get('type') == 'doc':
            doc = a.get('doc')
            if isinstance(doc, dict):
                return doc
    return None


def _extract_first_doc_attachment_from_message(message: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Extract first VK 'doc' attachment from a message.

    VK can put document attachments not only in the top-level "attachments", but also inside
    "reply_message" and "fwd_messages". If we don't look there, bot may silently ignore a message
    (especially in chats) and user sees 'no response'.
    """
    if not isinstance(message, dict):
        return None

    doc = _extract_first_doc_attachment(message.get('attachments', []))
    if doc:
        return doc

    reply = message.get('reply_message')
    if isinstance(reply, dict):
        doc = _extract_first_doc_attachment_from_message(reply)
        if doc:
            return doc

    fwd = message.get('fwd_messages')
    if isinstance(fwd, list):
        for m in fwd:
            if isinstance(m, dict):
                doc = _extract_first_doc_attachment_from_message(m)
                if doc:
                    return doc

    return None


def _ensure_doc_url(vk_helper, doc: Dict[str, Any]) -> Optional[str]:
    """Try to obtain direct URL for a VK doc attachment."""
    url = doc.get('url')
    if url:
        return url

    owner_id = doc.get('owner_id')
    doc_id = doc.get('id')
    access_key = doc.get('access_key')
    if owner_id is None or doc_id is None:
        return None

    try:
        docs_param = f"{owner_id}_{doc_id}" + (f"_{access_key}" if access_key else "")
        info = vk_helper.vk.docs.getById(docs=docs_param)
        if isinstance(info, list) and info:
            return info[0].get('url')
    except Exception:
        return None

    return None


def _upload_doc_to_vk(vk_helper, upload_peer_id: int, file_path: str, title: str) -> str:
    """Upload a local file into VK docs and return attachment string like doc<owner_id>_<id>."""
    # Timeouts: connect=5s, read=60s
    upload_url = vk_helper.vk.docs.getMessagesUploadServer(type='doc', peer_id=upload_peer_id)['upload_url']
    try:
        with open(file_path, 'rb') as f:
            resp = requests.post(upload_url, files={'file': f}, timeout=(5, 60))
    except requests.RequestException as e:
        raise RuntimeError(f"Не удалось загрузить файл на сервер VK: {e}")

    try:
        result = resp.json()
    except ValueError:
        raise RuntimeError("VK вернул некорректный ответ при загрузке файла (не JSON).")

    vk_file = result.get('file')
    if not vk_file:
        raise RuntimeError(f"VK вернул неожиданный ответ при загрузке файла: {result}")

    json_answer = vk_helper.vk.docs.save(file=vk_file, title=title, tags=[])
    doc = json_answer.get('doc') or (json_answer.get('doc', {}))
    if not isinstance(doc, dict) or 'owner_id' not in doc or 'id' not in doc:
        raise RuntimeError(f"VK вернул неожиданный ответ при сохранении файла: {json_answer}")
    return f"doc{doc['owner_id']}_{doc['id']}"


def process_message_event(event, vk_helper):
    payload = event.object.get('payload')
    user_list = UserList()
    metrics = Metrics()

    if not payload:
        return

    conversation_message_id = event.object['conversation_message_id']
    peer_id = event.object['peer_id']

    type_ = payload.get('type')
    sender = int(payload.get('sender'))

    if type_ in ['auto', 'send', 'approve', 'annul']:
        title = payload.get('title')
        tts = "Ваша служебная записка " + title
    else:
        tts = ""
        title = None

    if type_ == 'auto':
        tts += "\nпринята и отправлена на согласование!"
        buttons = [
            {
                "label": "ОТПРАВЛЕНО",
                "payload": {"type": "sended", "sender": sender, "title": title},
                "color": "positive"
            },
            {
                "label": "СОГЛАСОВАТЬ",
                "payload": {
                    "type": "approve",
                    "sender": sender,
                    "title": title,
                    "isSended": True
                },
                "color": "primary"
            },
            {
                "label": "АННУЛИРОВАТЬ",
                "payload": {"type": "annul", 'sender': sender, 'title': title, 'byAdmin': True},
                "color": "negative",
                "newline": True
            }
        ]
        keyboard = vk_helper.create_keyboard(buttons)
        vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

        title_with_marker = f'{title}'
        path = payload.get('path')

        club_name_start = title_with_marker.find("/СЗ_") + 4
        club_name_end = title_with_marker.find("_", club_name_start)
        club_name = title_with_marker[club_name_start:club_name_end]

        document_name = title_with_marker[club_name_end + 1:]
        if "." in document_name:
            document_name = document_name[:document_name.rfind(".")]

        mail = MailHelper()
        mail.send_mail(club_name, document_name, [path])

        doc_id = f"doc_{sender}_{uuid.uuid4().hex[:8]}"
        save_sent_document(doc_id, title_with_marker, sender, 'ITMO')

    elif type_ == "send":
        tts += "\nпринята и отправлена на согласование!"
        buttons = [
            {
                "label": "ОТПРАВЛЕНО",
                "payload": {"type": "sended", "sender": sender, "title": title},
                "color": "positive"
            },
            {
                "label": "СОГЛАСОВАТЬ",
                "payload": {
                    "type": "approve",
                    "sender": sender,
                    "title": title,
                    "isSended": True
                },
                "color": "primary"
            },
                {
                    "label": "АННУЛИРОВАТЬ",
                    "payload": {"type": "annul", 'sender': sender, 'title': title, 'byAdmin': True},
                    "color": "negative",
                    "newline": True
                }
        ]
        keyboard = vk_helper.create_keyboard(buttons)
        vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

    elif type_ == "approve":
        is_sended = payload.get('isSended')
        if is_sended:
            tts += "\nсогласована и внесена в систему для отображения на мониторе охраны!"
        else:
            tts += "\nсогласована и внесена в систему для получения QR на терминале!"

        buttons = [
            {
                "label": "ОТПРАВЛЕНО",
                "payload": {"type": "sended", "sender": sender, "title": title},
                "color": "positive"
            },
            {
                "label": "СОГЛАСОВАНО",
                "payload": {
                    "type": "approved",
                    "sender": sender,
                    "title": title,
                    "isSended": True
                },
                "color": "positive"
            }
        ]
        keyboard = vk_helper.create_keyboard(buttons)
        vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

        metrics.record_memo_approved(sender)

    elif type_ == "annul":
        by_admin = payload.get('byAdmin')
        managerflag = " МЕНЕДЖЕРОМ" if by_admin else ""
        tts += f" АННУЛИРОВАНА{managerflag}!"
        buttons = [
            {
                "label": "АННУЛИРОВАНО",
                "payload": {
                    "type": "annuled",
                    "sender": sender,
                    "title": title
                },
                "color": "negative"
            }
        ]
        keyboard = vk_helper.create_keyboard(buttons)
        vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

    elif type_ == "club":
        status = payload.get('status')
        club = payload.get('club')
        if status == "decline":
            tts += "Отмена! Отправь мне служебную записку с правильным названием."
        elif status == "accept":
            tts += f"Принято! Ты связал свой айди с клубом «{club}». Теперь отправь свою служебную записку заново"
            user_list.add(sender, club)
            keyboard = None
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)
    else:
        return

    return [{
        "peer_id": sender,
        "message": tts,
    }]


def process_message_new(event, vk_helper, ignored):
    info, error = log()
    tts = ''
    yonote = 'https://ursi.yonote.ru/share/clubs/doc/sluzhebnye-zapiski-i-prohod-gostej-bihQHvmk8w'

    user_list = UserList()
    user_list.load_from_file()
    metrics = Metrics()

    # --- график работы ---
    hour = int(str(date.now().time())[:2])
    weekday = date.today().weekday()
    month = int(str(date.now().date())[-5:-3])
    day = int(str(date.now().date())[-2:])
    if (month == 12 and day >= 28) or (month == 1 and day <= 8):
        tts += (
            "С новым годом! Служебные записки не согласуются на каникулах. Вы можете отправить документ, "
            "бот его обработает, но согласование получите только после 9 января. Если ситуация срочная, "
            "пишите \"МЕНЕДЖЕР\"\n\n"
        )
    elif weekday > 4:
        tts += (
            "Внимание! Служебные записки не согласуются по выходным. Вы можете отправить документ, "
            "бот его обработает, но согласование получите только в понедельник. Если ситуация срочная, "
            "пишите \"МЕНЕДЖЕР\"\n\n"
        )
    elif weekday == 4 and hour >= 16:
        tts += (
            "Внимание! По пятницам служебные записки не согласуются после 16:00. Вы можете отправить документ, "
            "бот его обработает, но согласование получите только в понедельник. Если ситуация срочная, "
            "пишите \"МЕНЕДЖЕР\"\n\n"
        )
    elif hour >= 17:
        tts += (
            "Внимание! Служебные записки не согласуются после 17:00. Вы можете отправить документ, "
            "бот его обработает, но согласование получите только завтра. Если ситуация срочная, "
            "пишите \"МЕНЕДЖЕР\"\n\n"
        )
    elif hour < 10:
        tts += (
            "Внимание! Служебные записки не обрабатываются до 10:00. Вы можете отправить документ, "
            "бот его обработает, но согласование получите только в рабочее время. Если ситуация срочная, "
            "пишите \"МЕНЕДЖЕР\"\n\n"
        )

    uid = event.message.from_id
    metrics.record_message(uid)

    msgraw = (event.message.text or "")
    msg = msgraw.lower()
    msgs = msg.split()

    # Имя/фамилия (не критично)
    uname = ""
    usurname = ""
    try:
        if uid > 0:
            user_get = vk_helper.vk.users.get(user_ids=uid)
            user_get = user_get[0]
            uname = user_get.get('first_name', '')
            usurname = user_get.get('last_name', '')
    except Exception:
        pass

    is_chat = bool(getattr(event, 'from_chat', False))
    incoming_peer_id = event.object.message.get('peer_id', uid)

    message_obj = event.object.message
    doc = _extract_first_doc_attachment_from_message(message_obj)

    # В чатах ничего не пишем. Реагируем только на документы/команды менеджера,
    # а ответы отправляем в ЛС.
    if is_chat and doc is None and not ("менеджер" in msg or "админ" in msg):
        return

    # Игнор-лист (режим вызова менеджера)
    if ignored.is_ignored(uid) and not ("менеджер" in msg or "админ" in msg):
        buttons = [{"label": "СПАСИБО МЕНЕДЖЕР", "payload": {"type": "uncallmanager"}, "color": "negative"}]
        keyboard = vk_helper.create_standart_keyboard(buttons)
        return [{
            "peer_id": uid,
            "message": tts + "Вы сейчас в режиме вызова менеджера (бот не обрабатывает записки).\n\n"
                             "Напишите проблему следующим сообщением. Когда вопрос будет решён — отправьте \"МЕНЕДЖЕР\" ещё раз "
                             "или нажмите кнопку ниже.",
            "keyboard": keyboard,
        }]

    # Команда менеджера
    if "менеджер" in msg or "админ" in msg:
        metrics.record_manager(uid)
        link = f"https://vk.com/gim{groupid}?sel={uid}"
        buttons = [{"label": "прямая ссылка", "payload": {"type": "userlink"}, "link": link}]
        link_keyboard = vk_helper.create_link_keyboard(buttons)

        if ignored.is_ignored(uid):
            ignored.remove(uid)
            ignored.save_to_file()
            tts_user = "Надеюсь, вопрос снят!"
            tts_chat = f"{uname} {usurname} больше не вызывает!"
            buttons = [{"label": "ПОЗВАТЬ МЕНЕДЖЕРА", "payload": {"type": "callmanager"}, "color": "positive"}]
            keyboard = vk_helper.create_standart_keyboard(buttons)
        else:
            ignored.add(uid)
            ignored.save_to_file()
            tts_user = (
                "Принято, сейчас позову! Напиши свою проблему следующим сообщением. "
                "Когда вопрос будет решён, ещё раз напиши команду или нажми на кнопку."
            )
            tts_chat = f"{uname} {usurname} вызывает!"
            buttons = [{"label": "СПАСИБО МЕНЕДЖЕР", "payload": {"type": "uncallmanager"}, "color": "negative"}]
            keyboard = vk_helper.create_standart_keyboard(buttons)

        return [
            {"peer_id": uid, "message": tts_user, "keyboard": keyboard, "attachment": None},
            {"peer_id": 2000000000 + admin_chat, "message": tts_chat, "keyboard": link_keyboard, "attachment": None},
        ]

    # Админ-команды (в ЛС; в чатах тоже отвечаем только в ЛС)
    if msgs and uid in admins:
        if msgs[0] == "stop":
            exit()
        elif msgs[0] == "stat":
            return [{"peer_id": uid, "message": metrics.get_report()}]
        elif msgs[0] == "sender" and len(msgs) >= 2:
            sender_type = msgs[1]
            text = msgraw[msgraw.find("\n"):] if "\n" in msgraw else ""
            tts_admin = f"Готово. Проверь текст и отправляй рассылку {sender_type}:\n\n{text}"
            buttons = [{
                "label": "ОТПРАВИТЬ РАССЫЛКУ",
                "payload": {"type": "sender", "sender": sender_type, "text": text},
                "color": "primary"
            }]
            keyboard = vk_helper.create_keyboard(buttons)
            return [{"peer_id": uid, "message": tts_admin, "keyboard": keyboard}]
        elif msgs[0] == "sync":
            mail_sync = MailSyncManager()
            result = mail_sync.force_sync()
            t = "Синхронизация почты выполнена." if result.get('status') == 'success' else f"Ошибка синхронизации: {result.get('message')}"
            return [{"peer_id": uid, "message": t}]
        elif msgs[0] == "mailstat":
            mail_sync = MailSyncManager()
            m = mail_sync.get_metrics()
            tts_admin = (
                "Метрики почты:\n"
                f"Получено писем: {m.get('emails_received', 0)}\n"
                f"Отправлено документов: {m.get('documents_sent', 0)}\n"
                f"Сопоставлено документов: {m.get('documents_reconciled', 0)}\n"
                f"Ошибок: {m.get('reconciliation_failed', 0)}\n"
                f"Последняя проверка: {m.get('last_check', 'Never')}"
            )
            return [{"peer_id": uid, "message": tts_admin}]

    # Если нет документа — отвечаем только в ЛС и только если это не чат
    if doc is None:
        if is_chat:
            return
        try:
            is_member = vk_helper.vk_session.method('groups.isMember', {'group_id': groupid, 'user_id': uid})
        except Exception:
            is_member = 1

        if is_member == 0:
            tts += (
                "Бот создан для предобработки служебных записок в университете ИТМО и доступен только клубам. "
                "Чтобы иметь доступ к обработке служебных записок необходимо подписаться на сообщество (ссылку "
                "можно найти в еноте или спросить в группе тг).\n\nПосле подписки отправь ещё одно сообщение. "
                "Только в случае возникновения проблем пиши \"МЕНЕДЖЕР\""
            )
        else:
            tts += (
                "Отправь мне служебную записку, я проведу предпроверку. Если всё хорошо, я отправлю её на обработку, "
                "после чего жди сообщения от менеджера. Если возникла проблема — пиши \"МЕНЕДЖЕР\"\n"
                "P.S. обязательно отправляй служебные записки в формате, указанном в yonote: " + yonote
            )
        return [{"peer_id": uid, "message": tts}]

    # --- обработка документа ---
    try:
        attachment_title = (doc.get('title') or "").strip()
        attachment_ext = (doc.get('ext') or "").lower().strip()

        # Ссылка на файл может отсутствовать в некоторых кейсах (пересылка/ограничения) — пробуем получить через API
        attachment_url = _ensure_doc_url(vk_helper, doc)
        if not attachment_url:
            metrics.record_memo_filtered(uid)
            return [{
                "peer_id": uid,
                "message": tts + "Не удалось получить прямую ссылку на документ от VK.\n"
                                 "Попробуйте отправить файл как 'Документ' (не пересылкой), либо скачайте и отправьте заново."
            }]

        # Валидация названия
        if (not re.match(CLUB_NAME_RE, attachment_title)) or ("шаблон" in attachment_title and uid not in admins):
            metrics.record_memo_filtered(uid)
            return [{
                "peer_id": uid,
                "message": tts + "Ошибка в названии файла. Пример:\nСЗ_ClubName.xlsx\n"
                                 "Допускается:\nСЗ_ClubName.метаинф.xlsx\n\n"
                                 "Название клуба — без пробелов; допустимы буквы/цифры/._- (лучше латиницей)."
            }]

        match = re.search(CLUB_NAME_RE, attachment_title)
        if not match:
            metrics.record_memo_filtered(uid)
            return [{"peer_id": uid, "message": tts + "Не удалось распознать название клуба из имени файла."}]

        title_marker = match.group()[3:]  # "<club>."
        club_name = title_marker[:-1]

        # Проверка подписки на группу (и для чатов тоже, но отвечаем только в ЛС)
        try:
            is_member = vk_helper.vk_session.method('groups.isMember', {'group_id': groupid, 'user_id': uid})
        except Exception:
            is_member = 1
        if is_member == 0:
            metrics.record_memo_filtered(uid)
            return [{
                "peer_id": uid,
                "message": tts + "Чтобы пользоваться ботом, подпишитесь на сообщество (ссылка в yonote/чате).\n"
                                 "После подписки отправьте документ ещё раз."
            }]

        if club_name not in user_list.get_clubs(uid):
            t_confirm = (
                f"Вы хотите связать свой аккаунт с клубом «{club_name}». В дальнейшем используйте одно название для всех СЗ_... "
                f"от одного клуба.\n\n"
                "Нажимая кнопку ПОДТВЕРДИТЬ и продолжая пользоваться сервисом вы соглашаетесь с правилами пользования и подтверждаете, что:\n"
                "1) данные в записках корректны и принадлежат реальным людям;\n"
                "2) клубы обязаны следить за своими гостями на территории университета;\n"
                "3) ознакомлены с графиком работы бота: пн-чт 10:00-17:00, пт 10:00-16:00;\n"
                f"4) знаете, где взять информацию о формате СЗ и командах бота: {yonote}.\n\n"
                "В случае нарушений этих простых правил клубу может быть полностью ограничен доступ к сервису."
            )
            buttons = [
                {"label": "ПОДТВЕРДИТЬ", "payload": {"type": "club", 'sender': uid, "status": "accept", "club": club_name}, "color": "positive"},
                {"label": "ОТМЕНИТЬ", "payload": {"type": "club", 'sender': uid, "status": "decline", "club": club_name}, "color": "negative"}
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            return [{"peer_id": uid, "message": tts + t_confirm, "keyboard": keyboard}]

        # Скачиваем исходный файл (с таймаутами и проверкой ответа)
        try:
            path = net_helper.attachment_extract(attachment_url, club_name, attachment_ext)
        except RuntimeError as e:
            metrics.record_memo_filtered(uid)
            return [{
                "peer_id": uid,
                "message": tts + "Не удалось скачать документ (возможна сетевая ошибка или VK не отдаёт файл).\n"
                                 "Попробуйте отправить документ ещё раз (не пересылкой). Если повторяется — напишите \"МЕНЕДЖЕР\".\n\n"
                                 f"Технические детали: {e}"
            }]

        if attachment_ext not in ['xlsx', 'docx']:
            metrics.record_memo_filtered(uid)
            return [{"peer_id": uid, "message": tts + "Поддерживаются только .xlsx и .docx"}]

        metrics.record_memo_received(uid)

        if attachment_ext == 'xlsx':
            try:
                check = check_excel(path)
            except Exception as exc:
                check = ["ER", exc]

            if check[0] != "success":
                metrics.record_memo_filtered(uid)
                if check[0] == "00":
                    tts_err = "Ошибка в одной из ячеек, которые нельзя менять. Перепроверьте A1, A2, B2, C1, C2, D2, E1, E2, F2, G1, G2, G3, H1 по шаблону."
                elif check[0] == "01":
                    tts_err = "Ошибка в одной из ячеек, которые необходимо было изменить. Поменяйте шаблон!"
                elif check[0] == "02":
                    tts_err = "Дата не может быть ранее сегодняшней!"
                elif check[0] == "ER":
                    tts_err = "Неопознанная ошибка, позовите менеджера: " + str(check[1])
                else:
                    tts_err = "Ошибка: " + str(check)
                return [{"peer_id": uid, "message": tts + tts_err}]

            rows = check[1]
            kolgost = int(float(rows[-1][0]))
            korpus = rows[0][1]
            data_ = rows[0][3]
            merotitle = rows[0][5]
            org = rows[1][7]
            orgnomer = str(rows[2][7])

            base_club = title_marker[:-1]
            newname_base = "СЗ_" + base_club + "_" + korpus[0] + korpus[-1] + "_" + "_".join(
                data_.replace(":", "-").replace(".", "-").split()
            )
            newname = newname_base
            newpath = "data/xlsx/" + newname + ".xlsx"
            for i in range(1, 999):
                if os.path.exists(newpath):
                    newname = f"{newname_base}({i})"
                    newpath = "data/xlsx/" + newname + ".xlsx"
                else:
                    break

            create_excel(newpath, rows)

            attachment_vk = _upload_doc_to_vk(vk_helper, incoming_peer_id, newpath, newname)
            user_msg = (
                tts + "Принято! Отправил на проверку, ожидайте ответа.\n"
                f"Проверьте данные. В случае несовпадений, вызовите менеджера:\n"
                f"Дата: {data_}\nорганизатор: {org} (+{orgnomer})\n"
                f"Название мероприятия: {merotitle}\nКорпус: {korpus}\nКоличество гостей: {kolgost}"
            )
            admin_msg = (
                f"новая проходка: vk.com/gim{groupid}?sel={uid}\n"
                f"дата: {data_}\nорганизатор: {org} (+{orgnomer})\n"
                f"количество гостей: {kolgost}\nназвание мероприятия: {merotitle}\nкорпус: {korpus}\n"
                f"отправитель: {uname} {usurname}"
            )
            title_for_buttons = newpath[5:]
            payload_path = newpath

        else:  # docx
            base_club = title_marker[:-1]
            newname_base = "СЗ_" + base_club + "_" + "_".join(str(date.now())[:-7].replace(":", "-").split())
            newname = newname_base
            newpath = "data/docx/" + newname + ".docx"
            for i in range(1, 999):
                if os.path.exists(newpath):
                    newname = f"{newname_base}({i})"
                    newpath = "data/docx/" + newname + ".docx"
                else:
                    break
            shutil.copy(path, newpath)
            attachment_vk = _upload_doc_to_vk(vk_helper, incoming_peer_id, newpath, newname)
            user_msg = tts + "Принято! Отправил на проверку, ожидайте ответа.\n"
            admin_msg = f"новая проходка: vk.com/gim{groupid}?sel={uid}\nотправитель: {uname} {usurname}"
            title_for_buttons = newpath[5:]
            payload_path = newpath

        buttons = [
            {"label": "АВТОСОГЛАСОВАНИЕ", "payload": {"type": "auto", 'sender': uid, 'title': title_for_buttons, 'path': payload_path}, "color": "secondary"},
            {"label": "ОТПРАВИТЬ", "payload": {"type": "send", 'sender': uid, 'title': title_for_buttons}, "color": "primary", "newline": True},
            {"label": "СОГЛАСОВАТЬ", "payload": {"type": "approve", 'sender': uid, 'title': title_for_buttons, 'isSended': False}, "color": "primary"},
            {"label": "АННУЛИРОВАТЬ", "payload": {"type": "annul", 'sender': uid, 'title': title_for_buttons, 'byAdmin': True}, "color": "negative", "newline": True},
        ]
        c_keyboard = vk_helper.create_keyboard(buttons)

        return [
            {"peer_id": uid, "message": user_msg, "keyboard": None, "attachment": attachment_vk},
            {"peer_id": 2000000000 + admin_chat, "message": admin_msg, "keyboard": c_keyboard, "attachment": attachment_vk},
        ]

    except Exception as e:
        error(f"Ошибка обработки документа от uid={uid}: {e}")
        metrics.record_memo_filtered(uid)
        return [{
            "peer_id": uid,
            "message": tts + "Не удалось обработать документ из-за внутренней/сетевой ошибки. "
                             "Пожалуйста, попробуйте отправить файл заново. Если повторяется — напишите \"МЕНЕДЖЕР\".\n\n"
                             f"Технические детали: {e}"
        }]
