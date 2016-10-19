#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains a object that represents a Telegram
InlineKeyboardButton"""

from telegram import TelegramObject


class InlineKeyboardButton(TelegramObject):
    """This object represents a Telegram InlineKeyboardButton.

    Attributes:
        text (str):
        url (str):
        callback_data (str):
        switch_inline_query (str):

    Args:
        text (str):
        url (Optional[str]):
        callback_data (Optional[str]):
        switch_inline_query (Optional[str]):
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self, text, url=None, callback_data=None, switch_inline_query=None, **kwargs):
        # Required
        self.text = text

        # Optionals
        self.url = url
        self.callback_data = callback_data
        self.switch_inline_query = switch_inline_query

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.InlineKeyboardButton:
        """
        data = super(InlineKeyboardButton, InlineKeyboardButton).de_json(data, bot)

        if not data:
            return None

        return InlineKeyboardButton(**data)

    @staticmethod
    def de_list(data, bot):
        if not data:
            return []

        inline_keyboards = list()
        for inline_keyboard in data:
            inline_keyboards.append(InlineKeyboardButton.de_json(inline_keyboard, bot))

        return inline_keyboards
