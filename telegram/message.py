#!/usr/bin/env python


class Message(object):
    def __init__(self,
                 message_id,
                 from_user,
                 date,
                 chat,
                 forward_from=None,
                 forward_date=None,
                 reply_to_message=None,
                 text=None,
                 audio=None,
                 document=None,
                 photo=None,
                 sticker=None,
                 video=None,
                 contact=None,
                 location=None,
                 new_chat_participant=None,
                 left_chat_participant=None,
                 new_chat_title=None,
                 new_chat_photo=None,
                 delete_chat_photo=None,
                 group_chat_created=None):
        self.message_id = message_id
        self.from_user = from_user
        self.date = date
        self.chat = chat
        self.forward_from = forward_from
        self.forward_date = forward_date
        self.reply_to_message = reply_to_message
        self.text = text
        self.audio = audio
        self.document = document
        self.photo = photo
        self.sticker = sticker
        self.video = video
        self.contact = contact
        self.location = location
        self.new_chat_participant = new_chat_participant
        self.left_chat_participant = left_chat_participant
        self.new_chat_title = new_chat_title
        self.new_chat_photo = new_chat_photo
        self.delete_chat_photo = delete_chat_photo
        self.group_chat_created = group_chat_created

    @property
    def chat_id(self):
        return self.chat.id

    @staticmethod
    def de_json(data):
        if 'from' in data:  # from is a reserved word, use user_from instead.
            from telegram import User
            from_user = User.de_json(data['from'])
        else:
            from_user = None

        if 'chat' in data:
            if 'username' in data['chat']:
                from telegram import User
                chat = User.de_json(data['chat'])
            if 'title' in data['chat']:
                from telegram import GroupChat
                chat = GroupChat.de_json(data['chat'])
        else:
            chat = None

        if 'forward_from' in data:
            from telegram import User
            forward_from = User.de_json(data['forward_from'])
        else:
            forward_from = None

        if 'reply_to_message' in data:
            reply_to_message = Message.de_json(data['reply_to_message'])
        else:
            reply_to_message = None

        if 'audio' in data:
            from telegram import Audio
            audio = Audio.de_json(data['audio'])
        else:
            audio = None

        if 'document' in data:
            from telegram import Document
            document = Document.de_json(data['document'])
        else:
            document = None

        if 'photo' in data:
            from telegram import PhotoSize
            photo = [PhotoSize.de_json(x) for x in data['photo']]
        else:
            photo = None

        if 'sticker' in data:
            from telegram import Sticker
            sticker = Sticker.de_json(data['sticker'])
        else:
            sticker = None

        if 'video' in data:
            from telegram import Video
            video = Video.de_json(data['video'])
        else:
            video = None

        if 'contact' in data:
            from telegram import Contact
            contact = Contact.de_json(data['contact'])
        else:
            contact = None

        if 'location' in data:
            from telegram import Location
            location = Location.de_json(data['location'])
        else:
            location = None

        if 'new_chat_participant' in data:
            from telegram import User
            new_chat_participant = User.de_json(data['new_chat_participant'])
        else:
            new_chat_participant = None

        if 'left_chat_participant' in data:
            from telegram import User
            left_chat_participant = User.de_json(data['left_chat_participant'])
        else:
            left_chat_participant = None

        return Message(message_id=data.get('message_id', None),
                       from_user=from_user,
                       date=data.get('date', None),
                       chat=chat,
                       forward_from=forward_from,
                       forward_date=data.get('forward_date', None),
                       reply_to_message=reply_to_message,
                       text=data.get('text', None),
                       audio=audio,
                       document=document,
                       photo=photo,
                       sticker=sticker,
                       video=video,
                       contact=contact,
                       location=location,
                       new_chat_participant=new_chat_participant,
                       left_chat_participant=left_chat_participant,
                       new_chat_title=data.get('new_chat_title', None),
                       new_chat_photo=data.get('new_chat_photo', None),
                       delete_chat_photo=data.get('delete_chat_photo', None),
                       group_chat_created=data.get('group_chat_created', None))
