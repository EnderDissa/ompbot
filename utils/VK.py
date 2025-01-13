from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api


class VK:
    def __init__(self, vk_session):
        self.vk_session = vk_session
        self.vk = vk_session.get_api()

    def lsend(self, id, text):
        print("sended to " + str(id))
        self.vk_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0})

    def lsend_withA(self, id, text, attachment):
        print("sended to " + str(id))
        self.vk_session.method('messages.send',
                               {'user_id': id, 'message': text, 'attachment': attachment, 'random_id': 0})

    def send(self, id, text):
        print("sended to " + str(id))
        self.vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})

    def send_withA(self, id, text, attachment, title, sender, kolgost=0):
        print("sended to " + str(id))
        keyboard = vk_api.keyboard.VkKeyboard(inline=True)
        keyboard.add_callback_button(label="ОТПРАВИТЬ", payload={"type": "send", 'sender': sender, 'title': title},
                                     color=VkKeyboardColor.SECONDARY)
        keyboard.add_callback_button(label="СОГЛАСОВАТЬ",
                                     payload={"type": "approve", 'sender': sender, 'title': title, 'isSended': False},
                                     color=VkKeyboardColor.POSITIVE)
        keyboard = keyboard.get_keyboard()
        self.vk_session.method('messages.send',
                               {'chat_id': id, 'message': text, 'attachment': attachment, 'keyboard': keyboard,
                                'random_id': 0})

    def editkb(self, peer_id, cmid, type, sender, title):
        keyboard = vk_api.keyboard.VkKeyboard(inline=True)
        keyboard.add_callback_button(label="ОТПРАВЛЕНО", payload={"type": "sended", 'sender': sender, 'title': title},
                                     color=VkKeyboardColor.NEGATIVE)
        keyboard.add_callback_button(label=("СОГЛАСОВАНО" if type == "approve" else "СОГЛАСОВАТЬ"),
                                     payload={"type": ("approved" if type == "approve" else "approve"),
                                              'sender': sender,
                                              'title': title, 'isSended': (False if type == "send" else True)},
                                     color=(
                                         VkKeyboardColor.NEGATIVE if type == "approved" else VkKeyboardColor.POSITIVE))
        keyboard = keyboard.get_keyboard()

        original_message = self.vk.messages.getById(
            peer_id=peer_id,
            cmids=cmid)
        original_text = original_message['items'][0]['text']
        original_attachment = original_message['items'][0]['attachments'][0]['doc']
        original_attachment = "doc" + str(original_attachment['owner_id']) + '_' + str(original_attachment['id'])

        self.vk.messages.edit(peer_id=peer_id, conversation_message_id=cmid, keyboard=keyboard, message=original_text,
                              attachment=original_attachment)

    def sender(self, sender_type):
        pass
