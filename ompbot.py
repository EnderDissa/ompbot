# -*- coding: utf-8 -*-
import json
import requests
from datetime import datetime as date
import re
from utils import check_excel, create_excel, IP


def process_message_event(event, vk_helper):
    pl = event.object.get('payload')
    if pl:
        conversation_message_id = event.object['conversation_message_id']
        peer_id = event.object['peer_id']

        type = pl['type']
        sender = int(pl['sender'])
        title = pl['title']

        tts = "Ваша служебная записка " + title

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
            keyboard=vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id,keyboard)

        elif type == "approve":
            is_sended = pl['isSended']
            if is_sended:
                tts += "\nсогласована и внесена в систему для отображения на мониторе охраны! Обращаем внимание на то, что клубы обязаны следить за своими гостями на территории университета, в частности не допускать их самостоятельного нахождения на территории вне мероприятия. В случае нарушений этого требования, клубу может быть полностью ограничен доступ к данному сервису."
            else:
                tts += "\nсогласована и внесена в систему для получения QR на терминале! Обращаем внимание на то, что клубы обязаны следить за своими гостями на территории университета, в частности не допускать их самостоятельного нахождения на территории вне мероприятия. В случае нарушений этого требования, клубу может быть полностью ограничен доступ к данному сервису."
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

        elif type=="annul":
            by_admin = pl['byAdmin']
            managerflag = " МЕНЕДЖЕРОМ" if by_admin else ""
            tts+=f" АННУЛИРОВАНА{managerflag}!"
            buttons = [
                {
                    "label": "АННУЛИРОВАНО",
                    "payload": {"type": "annuled", "sender": sender, "title": title},
                    "color": "negative"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
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
    peer_id = 2000000000 + uid
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
        link=f"https://vk.com/gim{groupid}?sel={uid}"
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
            tts = "Принято, сейчас позову! Напиши свою проблему следующим сообщением. "\
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
                    vk_helper.sender(msgs[1])
                    tts = "готово"
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

            path = IP.attachment_extract(attachment_url, attachment_title)

            check = check_excel(path)
            if check[0] == "success":
                rows = check[1]

                newname = "СЗ_" + attachment_title[:attachment_title.find(".")] + "_" + "_".join(
                    rows[0][3].replace(":", "-").replace(".", "-").split())
                newpath = "xlsx\\" + newname + ".xlsx"
                create_excel(newpath, rows)

                result = json.loads(requests.post(
                    vk_helper.vk.docs.getMessagesUploadServer(type='doc',
                                                             peer_id=event.object.message['peer_id'])[
                        'upload_url'],
                    files={'file': open(newpath, 'rb')}).text)
                jsonAnswer = vk_helper.vk.docs.save(file=result['file'], title=newname, tags=[])
                attachment = f"doc{jsonAnswer['doc']['owner_id']}_{jsonAnswer['doc']['id']}"

                kolgost = check[1][-1][0]
                korpus = check[1][0][1]
                data = check[1][0][3]
                merotitle = check[1][0][5]
                org = check[1][1][7]
                orgnomer = str(check[1][2][7])
                tts += f"Принято! Отправил на проверку, ожидайте ответа.\nПроверьте данные. В случае несовпадений, вызовите менеджера: организатор: {org} (+{orgnomer})" \
                       f"\nНазвание мероприятия: {merotitle}\nКорпус: {korpus}\nДата: {data} \nКоличество гостей:  {kolgost}"
                Сtts = f"новая проходка: vk.com/gim{groupid}?sel={uid}\nотправитель: {uname} {usurname}\nорганизатор: {org} (+{orgnomer})"\
                        f"\nназвание мероприятия: {merotitle}\nкорпус: {korpus}\nдата: {data} \nколичество гостей:  {kolgost}"
                newpath=newpath[5:]
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
                tts += "ошибка в одной из ячеек, которые нельзя менять."\
                       " перепроверьте A1, A2, B2, C1, C2, D2, E1, E2, F2, G1, G2, G3, H1 по шаблону"
            elif check[0] == "01":
                tts += "ошибка в одной из ячеек, которые необходимо было изменить. поменяйте шаблон!"
            else:
                tts += "ошибка в ячейке " + check
        return [{
            "peer_id": uid,
            "message": tts,
        }]
    return [{
        "peer_id": uid,
        "message": tts,
    }]

