# -*- coding: utf-8 -*-
import json

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent
import requests
import traceback
from datetime import datetime as date
import re
from utils import IgnoredList, VK, check_excel, create_excel, IP, initialize

token = initialize()

vk_session = vk_api.VkApi(token=token)
VK = VK(vk_session)

vk = vk_session.get_api()

yonote = 'https://ursi.yonote.ru/share/clubs/doc/sluzhebnye-zapiski-i-prohod-gostej-bihQHvmk8w'
groupid = 228288169
admin = [297002785]
ignored = IgnoredList()
ignored.load_from_file()

longpoll = VkBotLongPoll(vk_session, groupid)

print("работай")

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_EVENT:
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
                        VK.editkb(peer_id=peer_id, cmid=conversation_message_id, type="sended", sender=sender,
                                  title=title)
                    elif type == "approve":
                        is_sended = pl['isSended']
                        if is_sended:
                            tts += "\nсогласована и внесена в систему для отображения на мониторе охраны!"
                        else:
                            tts += "\nсогласована и внесена в систему для получения QR на терминале!"
                        VK.editkb(peer_id=peer_id, cmid=conversation_message_id, type="approved", sender=sender,
                                  title=title)
                    else:
                        continue

                    VK.lsend(sender, tts)
            if event.type == VkBotEventType.MESSAGE_NEW:
                tts = ''

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

                if event.from_chat:
                    id = event.chat_id
                    uid = event.obj['message']['from_id']
                    peer_id = 2000000000 + uid


                else:
                    uid = event.message.from_id

                    user_get = vk.users.get(user_ids=(uid))
                    user_get = user_get[0]
                    uname = user_get['first_name']
                    usurname = user_get['last_name']

                    peer_id = 2000000000 + uid
                    msg = event.object.message['text'].lower()
                    msgs = msg.split()
                    attachment = event.object.message['attachments']
                    if not attachment:
                        if vk_session.method('groups.isMember', {'group_id': groupid, 'user_id': uid}) == 0:
                            tts += "Бот создан для предобработки служебных записок в университете ИТМО и доступен только клубам. Поэтому чтобы иметь доступ к обработке служебных записок необходимо подписаться на это сообщество, ссылку ты можешь найти в еноте или спросить в группе тг!\n\nПосле подписки отправь ещё одно сообщение. Только в случае возникновения проблем пиши \"МЕНЕДЖЕР\""
                        else:
                            tts += "Отправь мне служебную записку, я проведу предпроверку. Если всё хорошо, я отправлю её на обработку, после чего жди сообщения от менеджера. Если возникла проблема, пиши \"МЕНЕДЖЕР\"\nP.S. обязательно отправляй служебные записки в формате, указанном в yonote: " + yonote

                    if msgs:
                        if uid in admin:
                            if msgs[0] == "stop":
                                exit()
                            elif msgs[0] == "sender":
                                sender(msgs[1])
                                tts = "готово"

                    if ignored.is_ignored(uid):
                        if not ("менеджер" in msg or "админ" in msg):
                            continue
                    if "менеджер" in msg or "админ" in msg:
                        if ignored.is_ignored(uid):
                            ignored.remove(uid)
                            ignored.save_to_file()
                            tts = "Надеюсь, вопрос снят!"
                            VK.send(1, uname + " " + usurname + " больше не вызывает. прямая ссылка:\nvk.com/gim" + str(
                                groupid) + "?sel=" + str(uid))
                        else:
                            ignored.add(uid)
                            ignored.save_to_file()
                            tts = "Принято, сейчас позову! Напиши свою проблему следующим сообщением. Когда вопрос будет решён, напиши команду ещё раз."
                            VK.send(1, uname + " " + usurname + " вызывает! прямая ссылка:\nvk.com/gim" + str(
                                groupid) + "?sel=" + str(uid))

                    else:
                        attachment = event.object.message['attachments']

                        if attachment:
                            attachment = attachment[0]
                            attachment = attachment['doc'] if attachment['type'] == 'doc' else None
                        else:
                            None

                        if attachment:
                            attachment_title = attachment['title']
                            attachment_ext = attachment['ext']
                            attachment_url = attachment['url']
                            if (not (re.match(r'СЗ_[а-яёА-ЯЁa-zA-Z]+\.', attachment_title))) or (
                                    "шаблон" in attachment_title and uid not in admin):
                                tts += "ошибка в названии файла. пример:\nСЗ_шаблон.xlsx\nдопускается:\nСЗ_шаблон.метаинф.xlsx\nВместо \"шаблон\" везде название клуба (без пробелов)."
                                VK.lsend(uid, tts)
                                continue
                            attachment_title = re.search(r'СЗ_[а-яёА-ЯЁa-zA-Z]+\.', attachment_title).group()[3:]

                            path = IP.attachment_extract(attachment_url, attachment_title)

                            check = check_excel(path)
                            if check[0] == "success":
                                rows = check[1]
                                tts += "Принято! Отправил на проверку, ожидайте ответа."
                                newname = "СЗ_" + attachment_title[:attachment_title.find(".")] + "_" + "_".join(
                                    rows[0][3].replace(":", "-").replace(".", "-").split())
                                newpath = "xlsx" + newname + ".xlsx"
                                create_excel(newpath, rows)

                                result = json.loads(requests.post(
                                    vk.docs.getMessagesUploadServer(type='doc',
                                                                    peer_id=event.object.message['peer_id'])[
                                        'upload_url'],
                                    files={'file': open(newpath, 'rb')}).text)
                                jsonAnswer = vk.docs.save(file=result['file'], title=newname, tags=[])
                                attachment = f"doc{jsonAnswer['doc']['owner_id']}_{jsonAnswer['doc']['id']}"

                                VK.lsend_withA(uid, tts, attachment)
                                kolgost = check[1][-1][0]
                                korpus = check[1][0][1]
                                data = check[1][0][3]
                                merotitle = check[1][0][5]
                                org = check[1][1][7]
                                orgnomer = str(check[1][2][7])
                                VK.send_withA(1, "новая проходка: vk.com/gim" + str(groupid) + "?sel=" + str(
                                    uid) + "\nотправитель: " + uname + " " + usurname + "\nорганизатор: " + org + "(" + orgnomer + ")" + "\nназвание мероприятия: " + merotitle + "\nкорпус: " + korpus + "\nдата: " + data + "\nколичество гостей: " + str(
                                    kolgost),
                                              attachment, newpath, uid, int(kolgost))

                                continue
                            elif check[0] == "00":
                                tts += "ошибка в одной из ячеек, которые нельзя менять. перепроверьте A1, A2, B2, C1, C2, D2, E1, E2, F2, G1, G2, G3, H1 по шаблону"
                            elif check[0] == "01":
                                tts += "ошибка в одной из ячеек, которые необходимо было изменить. поменяйте шаблон!"
                            else:
                                tts += "ошибка в ячейке " + check

                    VK.lsend(uid, tts)
    except Exception as e:
        print(e)
        traceback.print_exc()
