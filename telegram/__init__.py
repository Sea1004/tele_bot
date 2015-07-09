#!/usr/bin/env python
# flake8: noqa

"""A library that provides a Python interface to the Telegram Bots API"""

__author__ = 'leandrotoledodesouza@gmail.com'
__version__ = '1.1'

import json

from user import User
from message import Message
from update import Update
from groupchat import GroupChat
from photosize import PhotoSize
from audio import Audio
from document import Document
from sticker import Sticker
from video import Video
from contact import Contact
from location import Location
from chataction import ChatAction
from userprofilephotos import UserProfilePhotos
from replykeyboardmarkup import ReplyKeyboardMarkup
from replykeyboardhide import ReplyKeyboardHide
from forcereply import ForceReply
from replymarkup import ReplyMarkup
from error import TelegramError
from emoji import Emoji
from bot import Bot
