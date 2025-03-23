# -*- coding: utf-8 -*-
import json
import requests
from datetime import datetime as date
import re
from utils import check_excel, create_excel, IP
import os

from utils.Metrics import Metrics
from utils.user_list import UserList


def process_message_event(event, vk_helper):
    pl = event.object.get('payload')
    user_list = UserList()
    metrics = Metrics()
    if pl:
        conversation_message_id = event.object['conversation_message_id']
        peer_id = event.object['peer_id']

        type = pl['type']
        sender = int(pl['sender'])
        if type in ['send','approve', 'annul']:
            title = pl['title']
            tts = "Ваша служебная записка " + title
        else: tts=""

        if type == "send":
            tts += "\n принята и отправлена на согласование!"
            buttons = [
                {
                    "label": "ОТПРАВЛЕНО",
                    "payload": {"type": "sended", "sender": sender, "title": title},
                    "color": "positive"
                },
                {
                    "label": "СОГЛАСОВАТЬ",
                    "payload": {"type": "approve", "sender": sender, "title": title, "isSended": True},
                    "color": "primary"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

        elif type == "approve":
            is_sended = pl['isSended']
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
                    "payload": {"type": "approved", "sender": sender, "title": title, "isSended": True},
                    "color": "positive"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

            metrics.record_saved

        elif type == "annul":
            by_admin = pl['byAdmin']
            managerflag = " МЕНЕДЖЕРОМ" if by_admin else ""
            tts += f" АННУЛИРОВАНА{managerflag}!"
            buttons = [
                {
                    "label": "АННУЛИРОВАНО",
                    "payload": {"type": "annuled", "sender": sender, "title": title},
                    "color": "negative"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)
        elif type=="club":
            status=pl['status']
            club=pl['club']
            if status=="decline":
                tts+="Отмена! Отправь мне служебную записку с правильным названием."
            elif status=="accept":
                tts+=f"Принято! Ты связал свой айди с клубом «{club}». Теперь отправь свою служебную записку заново"
                user_list.add(sender,club)
            keyboard = None
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)


        else:
            return
    return [{
        "peer_id": sender,
        "message": tts,
    }]


def process_message_new(event, vk_helper, ignored):
    tts = ''
    yonote = 'https://ursi.yonote.ru/share/clubs/doc/sluzhebnye-zapiski-i-prohod-gostej-bihQHvmk8w'
    groupid = 228288169
    admin = [297002785]
    user_list = UserList()
    user_list.load_from_file()
    metrics= Metrics()


    time = int(str(date.now().time())[:2])
    weekday = date.today().weekday()
    month = int(str(date.now().date())[-5:-3])
    day = int(str(date.now().date())[-2:])
    if (month == 12 and day >= 28) or (month == 1 and day <= 8):
        tts += "С новым годом! Служебные записки не согласуются на каникулах. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только после 9 января. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif weekday > 4:
        tts += "Внимание! Служебные записки не согласуются по выходным. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только в понедельник. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif weekday == 4 and time >= 16:
        tts += "Внимание! По пятницам служебные записки не согласуются после 16:00. Вы можете отправить " \
               "документ, бот его обработает, но согласование получите только в понедельник. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif time >= 17:
        tts += "Внимание! Служебные записки не согласуются после 17:00. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только завтра. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif time < 10:
        tts += "Внимание! Служебные записки не обрабатываются до 10:00. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только в рабочее время. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"

    uid = event.message.from_id
    metrics.record_message(uid)
    peer_id = 2000000000 + uid
    msgraw = event.message.text
    msg = event.message.text.lower()
    msgs = msg.split()

    user_get = vk_helper.vk.users.get(user_ids=uid)
    user_get = user_get[0]
    uname = user_get['first_name']
    usurname = user_get['last_name']
    if ignored.is_ignored(uid):
        if not ("менеджер" in msg or "админ" in msg):
            return

    if "менеджер" in msg or "админ" in msg:
        metrics.record_manager(uid)
        link = f"https://vk.com/gim{groupid}?sel={uid}"
        buttons = [{"label": "прямая ссылка", "payload": {"type": "userlink"}, "link": link}]
        link_keyboard = vk_helper.create_link_keyboard(buttons)
        if ignored.is_ignored(uid):
            ignored.remove(uid)
            ignored.save_to_file()
            tts = "Надеюсь, вопрос снят!"
            Сtts = f"{uname} {usurname} больше не вызывает!"
            buttons = [{"label": "ПОЗВАТЬ МЕНЕДЖЕРА", "payload": {"type": "callmanager"}, "color": "positive"}]
            keyboard = vk_helper.create_standart_keyboard(buttons)

        else:
            ignored.add(uid)
            ignored.save_to_file()
            tts = "Принято, сейчас позову! Напиши свою проблему следующим сообщением. " \
                  "Когда вопрос будет решён, ещё раз напиши команду или нажми на кнопку."
            Сtts = f"{uname} {usurname} вызывает!"
            buttons = [{"label": "СПАСИБО МЕНЕДЖЕР", "payload": {"type": "uncallmanager"}, "color": "negative"}]
            keyboard = vk_helper.create_standart_keyboard(buttons)
        return [
            {
                "peer_id": uid,
                "message": tts,
                "keyboard": keyboard,
                "attachment": None
            },
            {
                "peer_id": 2000000000 + 1,
                "message": Сtts,
                "keyboard": link_keyboard,
                "attachment": None
            }
        ]

    if event.from_chat:
        id = event.chat_id
        uid = event.obj['message']['from_id']
        peer_id = 2000000000 + uid
        return

    else:
        attachment = event.object.message['attachments']
        if not attachment:
            if vk_helper.vk_session.method('groups.isMember', {'group_id': groupid, 'user_id': uid}) == 0:
                tts += "Бот создан для предобработки служебных записок в университете ИТМО и доступен только клубам. " \
                       "Поэтому чтобы иметь доступ к обработке служебных записок необходимо подписаться на это " \
                       "сообщество, ссылку ты можешь найти в еноте или спросить в группе тг!\n\nПосле подписки " \
                       "отправь ещё одно сообщение. Только в случае возникновения проблем пиши \"МЕНЕДЖЕР\""
            else:
                tts += "Отправь мне служебную записку, я проведу предпроверку. Если всё хорошо, я отправлю её на " \
                       "обработку, после чего жди сообщения от менеджера. Если возникла проблема, " \
                       "пиши \"МЕНЕДЖЕР\"\nP.S. обязательно отправляй служебные записки в формате, указанном в " \
                       "yonote: " + yonote
        if msgs:
            if uid in admin:
                if msgs[0] == "stop":
                    exit()
                elif msgs[0] == "sender":
                    sender_type = msgs[1]
                    text = msgraw[msgraw.find("\n"):]
                    tts = f"Готово. Проверь текст и отправляй рассылку {sender_type}:\n\n{text}"
                    buttons = [{"label": "ОТПРАВИТЬ РАССЫЛКУ",
                                "payload": {"type": "sender", "sender": sender_type, "text": text}, "color": "primary"}]
                    keyboard = vk_helper.create_keyboard(buttons)
                    return [{
                        "peer_id": uid,
                        "message": tts,
                        "keyboard": keyboard
                    }]
        attachment = event.object.message['attachments']
        if attachment:
            attachment = attachment[0]
            attachment = attachment['doc'] if attachment['type'] == 'doc' else None
            attachment_title = attachment['title']
            attachment_ext = attachment['ext']
            attachment_url = attachment['url']
            if (not (re.match(r'СЗ_[а-яёА-ЯЁa-zA-Z]+\.', attachment_title))) or (
                    "шаблон" in attachment_title and uid not in admin):
                tts += "ошибка в названии файла. пример:\nСЗ_шаблон.xlsx\nдопускается:\nСЗ_шаблон.метаинф.xlsx\n" \
                       "Вместо \"шаблон\" везде название клуба (без пробелов, лучше латиницей)."
                return [{
                    "peer_id": uid,
                    "message": tts,
                }]
            attachment_title = re.search(r'СЗ_[а-яёА-ЯЁa-zA-Z]+\.', attachment_title).group()[3:]
            club_name=attachment_title[:-1]


            if club_name not in user_list.get_clubs(uid):
                tts+=f"Вы хотите связать свой аккаунт с клубом «{club_name}». Обратите внимание, если до этого уже связывали аккаунт с клубом, но сейчас написали другое название в СЗ, отправьте корректную записку или вызовите менеджера. Используйте одно название для всех СЗ_название.\nНажимая кнопку ПОДТВЕРДИТЬ и продолжая пользоваться сервисом вы соглашаетесь с правилами пользования сервисом и подтверждаете, что:\n1) данные в записках корректны и принадлежат реальным людям.\n2) знаете: клубы обязаны следить за своими гостями на территории университета, в частности не допускать их самостоятельного нахождения на территории вне мероприятия.\n3) ознакомлены с графиком работы бота: пн-чт 10:00-17:00, пт 10:00-16:00. В остальное время записки не обрабатываются, так как не работает ни УФБ, ни ОМП. За редким исключением, вашу служебную записку будет некому обработать (при этом отправлять заранее можно и нужно)\n5) знаете, где взять информацию о формате СЗ и командах бота: https://ursi.yonote.ru/share/clubs/doc/sluzhebnye-zapiski-i-prohod-gostej-bihQHvmk8w. \n\nВ случае нарушений этих простых правил, клубу может быть полностью ограничен доступ к сервису."
                buttons = [
                    {"label": "ПОДТВЕРДИТЬ", "payload": {"type": "club",'sender': uid, "status":"accept","club":club_name}, "color": "positive"},
                    {"label": "ОТМЕНИТЬ", "payload": {"type": "club",'sender': uid,"status":"decline","club":club_name}, "color": "negative"}
                ]
                keyboard = vk_helper.create_keyboard(buttons)
                return [{
                        "peer_id": uid,
                        "message": tts,
                        "keyboard": keyboard
                    }]

            path = IP.attachment_extract(attachment_url, attachment_title)

            try:
                check = check_excel(path)
            except Exception as exc:
                check = ["ER", exc]
            if check[0] == "success":
                rows = check[1]
                kolgost = int(float(rows[-1][0]))
                korpus = rows[0][1]
                data = rows[0][3]
                merotitle = rows[0][5]
                org = rows[1][7]
                orgnomer = str(rows[2][7])

                newname = "СЗ_" + attachment_title[:attachment_title.find(".")] + "_"+korpus[0]+korpus[-1]+"_" + "_".join(
                    rows[0][3].replace(":", "-").replace(".", "-").split())
                newpath = "xlsx\\" + newname + ".xlsx"
                if os.path.exists(newpath):
                    newname+="(1)"
                    newpath = "xlsx\\" + newname + ".xlsx"

                create_excel(newpath, rows)

                result = json.loads(requests.post(
                    vk_helper.vk.docs.getMessagesUploadServer(type='doc',
                                                              peer_id=event.object.message['peer_id'])[
                        'upload_url'],
                    files={'file': open(newpath, 'rb')}).text)
                jsonAnswer = vk_helper.vk.docs.save(file=result['file'], title=newname, tags=[])
                attachment = f"doc{jsonAnswer['doc']['owner_id']}_{jsonAnswer['doc']['id']}"


                tts += f"Принято! Отправил на проверку, ожидайте ответа.\nПроверьте данные. В случае несовпадений, вызовите менеджера: \nДата: {data}\nорганизатор: {org} (+{orgnomer})" \
                       f"\nНазвание мероприятия: {merotitle}\nКорпус: {korpus} \nКоличество гостей:  {kolgost}"
                Сtts = f"новая проходка: vk.com/gim{groupid}?sel={uid}\nдата: {data}\nорганизатор: {org} (+{orgnomer})" \
                       f"\nколичество гостей:  {kolgost}\nназвание мероприятия: {merotitle}\nкорпус: {korpus} \nотправитель: {uname} {usurname}"
                newpath = newpath[5:]
                buttons = [
                    {
                        "label": "ОТПРАВИТЬ",
                        "payload": {"type": "send", 'sender': uid, 'title': newpath},
                        "color": "primary"
                    },
                    {
                        "label": "СОГЛАСОВАТЬ",
                        "payload": {"type": "approve", 'sender': uid, 'title': newpath, 'isSended': False},
                        "color": "primary"
                    },
                    {
                        "label": "АННУЛИРОВАТЬ",
                        "payload": {"type": "annul", 'sender': uid, 'title': newpath, 'byAdmin': True},
                        "color": "negative",
                        "newline": True
                    }
                ]
                Ckeyboard = vk_helper.create_keyboard(buttons)

                # buttons = [{"label": "ОТМЕНИТЬ", "payload": {"type": "annul", 'sender': uid, 'title': newpath, 'byAdmin': False}, "color": "secondary"}]
                # keyboard = vk_helper.create_keyboard(buttons)
                # todo: сделать синхронизацию, чтобы можно было отменять со стороны пользователя
                return [
                    {
                        "peer_id": uid,
                        "message": tts,
                        "keyboard": None,
                        "attachment": attachment
                    },
                    {
                        "peer_id": 2000000000 + 1,
                        "message": Сtts,
                        "keyboard": Ckeyboard,
                        "attachment": attachment
                    }
                ]
            elif check[0] == "00":
                tts += "ошибка в одной из ячеек, которые нельзя менять." \
                       " перепроверьте A1, A2, B2, C1, C2, D2, E1, E2, F2, G1, G2, G3, H1 по шаблону"
            elif check[0] == "01":
                tts += "ошибка в одной из ячеек, которые необходимо было изменить. поменяйте шаблон!"
            elif check[0] == "ER":
                tts += "неопознанная ошибка, позовите менеджера: " + str(check[1])
            else:
                tts += "ошибка в ячейке " + check
        return [{
            "peer_id": uid,
            "message": tts,
        }]
