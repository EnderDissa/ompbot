# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime

import vk_api
from random import randint as rd

from openpyxl.styles import PatternFill, Side, Border
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import pandas as pd
import requests
import traceback
from datetime import datetime as date
import openpyxl
import re

def lsend(id, text):
    print("sended to "+str(id))
    vk_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0})
def lsend_withA(id, text, attachment):
    print("sended to " + str(id))
    vk_session.method('messages.send', {'user_id': id, 'message': text, 'attachment':attachment, 'random_id': 0})

def send(id,text):
    print("sended to " + str(id))
    vk_session.method('messages.send',{'chat_id':id,'message':text,'random_id':0})

def send_withA(id, text, attachment):
    print("sended to " + str(id))
    vk_session.method('messages.send', {'chat_id': id, 'message': text, 'attachment':attachment, 'random_id': 0})
def sender(sender_type):
   pass
def attachment_extract(url, name):
    response = requests.get(url)
    if not os.path.exists('xlsx/'+name[:-5]):
        dir='xlsx/'+name[:-5]
        os.mkdir(dir)
        print("новый клуб: "+name[:-5])
    path="xlsx/"+name[:-5]+"/"+("_".join(str(date.now())[:-7].replace(":","-").split()))+".xlsx"
    with open(path, "wb") as f:
        f.write(response.content)
        return path

def check_excel(path):
    row = []
    rows = []
    data = openpyxl.load_workbook(path)
    sheet = data.active
    correct_meta=['Корпус:', '№', 'Фамилия', 'Дата, время:', 'Имя', 'Отчество', 'Название мероприятия:', 'Серия и номер паспорта', 'Номер телефона', 'Ответственный от подразделения:', 'Ежков Павел Игроевич, заместитель директора ОМП', 89213422059, 'Контактное лицо:']
    meta = [sheet['A1'].value, sheet['A2'].value, sheet['B2'].value,sheet['C1'].value, sheet['C2'].value, sheet['D2'].value, sheet['E1'].value, sheet['E2'].value, sheet['F2'].value, sheet['G1'].value,sheet['G2'].value,sheet['G3'].value,sheet['H1'].value]
    korpus = sheet['B1'].value
    date_time = str(sheet['D1'].value)
    name = sheet['F1'].value
    rukovod = sheet['H2'].value
    rukovod_phone = sheet['H3'].value

    date = date_time.split()[0]
    #print(meta)
    #print(korpus, date_time, date, name, rukovod, rukovod_phone)
    if correct_meta==meta:
        i=0;cyrillic_lower_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        while True:
            i+=1
            col=str(i)
            if sheet['A' + col].value is None: break
            row=[sheet['A'+col].value,sheet['B'+col].value.strip(),sheet['C'+col].value.strip(),str(sheet['D'+col].value).strip(),str(sheet['E'+col].value).strip().zfill(10),str(sheet['F'+col].value).strip(),sheet['G'+col].value,sheet['H'+col].value]

            if i<3:
                rows.append(row)
                continue
            if row[0]!=i-2: return "A"+col
            for _ in row[1].lower():
                if _ not in cyrillic_lower_letters: return "B"+col
            for _ in row[2].lower():
                if _ not in cyrillic_lower_letters: return "C" + col+_
            for _ in str(row[3]).lower():
                if _ not in cyrillic_lower_letters: return "D" + col
            if not(row[4].isdigit()): return "E"+col
            phone=re.findall(r"(?:(?:8|\+7)[\- ]?)?(?:\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}",row[5])
            significant_digits = []
            digits = re.findall(r"\d", phone[0])
            significant_digits.extend(digits)
            print(significant_digits)
        if not phone: return "F"+col
        rows.append(row)
    else:
        return "00", rows

    return "success", rows



def create_excel(path, rows):
    data=openpyxl.Workbook()
    sheet = data.active

    sheet.title="Согласование СЗ"
    fill =  PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    border = Border(
        left=Side(border_style="medium", color='FF000000'),
        right=Side(border_style="medium", color='FF000000'),
        top=Side(border_style="medium", color='FF000000'),
        bottom=Side(border_style="medium", color='FF000000'),
        diagonal=Side(border_style="medium", color='FF000000'),
        diagonal_direction=0,
        outline=Side(border_style="medium", color='FF000000'),
        vertical=Side(border_style="medium", color='FF000000'),
        horizontal=Side(border_style="medium", color='FF000000')
    )

    for i in range(len(rows)):
        for j in range(len(rows[i])):
            cell=sheet.cell(row=i+1,column=j+1)
            cell.value=rows[i][j]
            if cell.value:
                cell.border = border

    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column_letter].width = adjusted_width

    sheet["A1"].fill = fill
    sheet["C1"].fill = fill
    sheet["E1"].fill = fill
    sheet["G1"].fill = fill
    sheet["H1"].fill = fill
    sheet["A2"].fill = fill
    sheet["B2"].fill = fill
    sheet["C2"].fill = fill
    sheet["D2"].fill = fill
    sheet["E2"].fill = fill
    sheet["F2"].fill = fill
    sheet["G2"].fill = fill
    sheet["G3"].fill = fill
    try:
        data.save(path)
        return True
    except:
        print("ERROR")
        return False



with open("token.txt", 'r') as f:
    token = f.readline()

vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()

groupid = 228288169
admin = [297002785]; ignore = []
longpoll = VkBotLongPoll(vk_session, groupid)


print("работай")




while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_chat:
                    id = event.chat_id
                    uid = event.obj['message']['from_id']
                    peer_id = 2000000000 + uid

                else:
                    uid = event.message.from_id
                    peer_id = 2000000000 + uid
                    msg = event.object.message['text'].lower()
                    msgs = msg.split()
                    if vk_session.method('groups.isMember', {'group_id': groupid, 'user_id': uid}) == 0:
                        tts = "Привет! Бот создан для предобработки служебных записок в университете ИТМО и доступен только клубам. Поэтому чтобы иметь доступ к обработке служебок необходимо подписаться на это сообщество, ссылку ты можешь найти в еноте или спросить в группе тг!\n\nПосле подписки отправь ещё одно сообщение. Только в случае возникновения проблем пиши \"АДМИН\""
                    else:
                        tts = "Здравствуй! Отправь мне служебку, я её предпроверю. Если всё хорошо, я отправлю её на обработку, после чего жди сообщения от менеджера.\nP.S. обязательно отправляй служебки в формате, указанном в еноте! (теперь эксель)"

                    if msgs:
                        if uid in admin:
                            if msgs[0] == "stop":
                                exit()
                            elif msgs[0] == "sender":
                                sender(msgs[1])
                                tts = "готово"

                    if "админ" in msg:
                        if uid in ignore:
                            ignore.remove(uid)
                            tts = "Надеюсь, вопрос снят!"
                            send(1, "vk.com/gim"+str(groupid)+"?sel=" + str(uid) + " не вызывает")
                        else:
                            ignore.append(uid)
                            tts = "Принято, сейчас позову! Напиши свою проблему следующим сообщением"
                            send(1, "vk.com/gim"+str(groupid)+"?sel=" + str(uid) + " вызывает")
                        lsend(uid, tts)


                    if uid in ignore:
                        continue
                    else:
                        attachment=event.object.message['attachments']

                        if attachment:
                            attachment=attachment[0]
                            attachment = attachment['doc'] if attachment['type'] == 'doc' else None
                        else: None

                        if attachment:
                            attachment_title=attachment['title']
                            attachment_ext=attachment['ext']
                            attachment_url=attachment['url']
                            path=attachment_extract(attachment_url, attachment_title[3:])


                            check=check_excel(path)
                            if check[0]=="success":
                                rows=check[1]
                                tts="принято:"
                                newname=attachment_title[:-5]+"_"+"_".join(rows[0][3].replace(":","-").split())
                                newpath = newname+".xlsx"
                                create_excel(newpath, rows)

                                result = json.loads(requests.post(
                                    vk.docs.getMessagesUploadServer(type='doc', peer_id=event.object.message['peer_id'])['upload_url'],
                                    files={'file': open(newpath, 'rb')}).text)
                                jsonAnswer = vk.docs.save(file=result['file'], title=newname, tags=[])
                                attachment = f"doc{jsonAnswer['doc']['owner_id']}_{jsonAnswer['doc']['id']}"

                                lsend_withA(uid,tts,attachment)
                                send_withA(1,"новая проходка от vk.com/gim"+str(groupid)+"?sel=" + str(uid), attachment)
                                continue
                            elif check[0]=="00":
                                tts="ошибка в одной из ячеек, которые нельзя менять. перепроверьте A1, A2, B2, C1, C2, D2, E1, E2, F2, G1, G2, G3, H1 по шаблону"
                            else: tts="ошибка в ячейке "+check


                    lsend(uid, tts)
    except Exception:
        traceback.print_exc()