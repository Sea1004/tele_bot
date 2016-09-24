#!/usr/bin/env python
# encoding: utf-8
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""
This module contains a object that represents Tests for ConversationHandler
"""
import logging
import sys
import unittest
from time import sleep

try:
    # python2
    from urllib2 import urlopen, Request, HTTPError
except ImportError:
    # python3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

sys.path.append('.')

from telegram import Update, Message, TelegramError, User, Chat, Bot
from telegram.ext import Updater, ConversationHandler, CommandHandler
from tests.base import BaseTest
from tests.test_updater import MockBot

# Enable logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARN)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s ' '- %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class ConversationHandlerTest(BaseTest, unittest.TestCase):
    """
    This object represents the tests for the conversation handler.
    """

    # State definitions
    # At first we're thirsty.  Then we brew coffee, we drink it
    # and then we can start coding!
    END, THIRSTY, BREWING, DRINKING, CODING = range(-1, 4)
    _updater = None

    # Test related
    def setUp(self):
        self.current_state = dict()
        self.entry_points = [CommandHandler('start', self.start)]
        self.states = {self.THIRSTY: [CommandHandler('brew', self.brew),
                                      CommandHandler('wait', self.start)],
                       self.BREWING: [CommandHandler('pourCoffee', self.drink)],
                       self.DRINKING: [CommandHandler('startCoding', self.code),
                                       CommandHandler('drinkMore', self.drink)],
                       self.CODING: [CommandHandler('keepCoding', self.code),
                                     CommandHandler('gettingThirsty', self.start),
                                     CommandHandler('drinkMore', self.drink)],}
        self.fallbacks = [CommandHandler('eat', self.start)]

    def _setup_updater(self, *args, **kwargs):
        bot = MockBot(*args, **kwargs)
        self.updater = Updater(workers=2, bot=bot)

    def tearDown(self):
        if self.updater is not None:
            self.updater.stop()

    @property
    def updater(self):
        return self._updater

    @updater.setter
    def updater(self, val):
        if self._updater:
            self._updater.stop()
        self._updater = val

    def reset(self):
        self.current_state = dict()

    # State handlers
    def _set_state(self, update, state):
        self.current_state[update.message.from_user.id] = state
        return state

    def _get_state(self, user_id):
        return self.current_state[user_id]

    # Actions
    def start(self, bot, update):
        return self._set_state(update, self.THIRSTY)

    def start_end(self, bot, update):
        return self._set_state(update, self.END)

    def brew(self, bot, update):
        return self._set_state(update, self.BREWING)

    def drink(self, bot, update):
        return self._set_state(update, self.DRINKING)

    def code(self, bot, update):
        return self._set_state(update, self.CODING)

    # Tests
    def test_addConversationHandler(self):
        self._setup_updater('', messages=0)
        d = self.updater.dispatcher
        user = User(first_name="Misses Test", id=123)
        second_user = User(first_name="Mister Test", id=124)

        handler = ConversationHandler(
            entry_points=self.entry_points, states=self.states, fallbacks=self.fallbacks)
        d.add_handler(handler)
        queue = self.updater.start_polling(0.01)

        # User one, starts the state machine.
        message = Message(0, user, None, None, text="/start")
        queue.put(Update(update_id=0, message=message))
        sleep(.1)
        self.assertTrue(self.current_state[user.id] == self.THIRSTY)

        # The user is thirsty and wants to brew coffee.
        message = Message(0, user, None, None, text="/brew")
        queue.put(Update(update_id=0, message=message))
        sleep(.1)
        self.assertTrue(self.current_state[user.id] == self.BREWING)

        # Lets see if an invalid command makes sure, no state is changed.
        message = Message(0, user, None, None, text="/nothing")
        queue.put(Update(update_id=0, message=message))
        sleep(.1)
        self.assertTrue(self.current_state[user.id] == self.BREWING)

        # Lets see if the state machine still works by pouring coffee.
        message = Message(0, user, None, None, text="/pourCoffee")
        queue.put(Update(update_id=0, message=message))
        sleep(.1)
        self.assertTrue(self.current_state[user.id] == self.DRINKING)

        # Let's now verify that for another user, who did not start yet,
        # the state has not been changed.
        message = Message(0, second_user, None, None, text="/brew")
        queue.put(Update(update_id=0, message=message))
        sleep(.1)
        self.assertRaises(KeyError, self._get_state, user_id=second_user.id)

    def test_endOnFirstMessage(self):
        self._setup_updater('', messages=0)
        d = self.updater.dispatcher
        user = User(first_name="Misses Test", id=123)

        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_end)], states={}, fallbacks=[])
        d.add_handler(handler)
        queue = self.updater.start_polling(0.01)

        # User starts the state machine and immediately ends it.
        message = Message(0, user, None, None, text="/start")
        queue.put(Update(update_id=0, message=message))
        sleep(.1)
        self.assertEquals(len(handler.conversations), 0)

    def test_endOnFirstMessageAsync(self):
        self._setup_updater('', messages=0)
        d = self.updater.dispatcher
        user = User(first_name="Misses Test", id=123)

        start_end_async = (lambda bot, update: d.run_async(self.start_end, bot, update))

        handler = ConversationHandler(
            entry_points=[CommandHandler('start', start_end_async)], states={}, fallbacks=[])
        d.add_handler(handler)
        queue = self.updater.start_polling(0.01)

        # User starts the state machine with an async function that immediately ends the
        # conversation. Async results are resolved when the users state is queried next time.
        message = Message(0, user, None, None, text="/start")
        queue.put(Update(update_id=0, message=message))
        sleep(.1)
        # Assert that the Promise has been accepted as the new state
        self.assertEquals(len(handler.conversations), 1)

        message = Message(0, user, None, None, text="resolve promise pls")
        queue.put(Update(update_id=0, message=message))
        sleep(.1)
        # Assert that the Promise has been resolved and the conversation ended.
        self.assertEquals(len(handler.conversations), 0)


if __name__ == '__main__':
    unittest.main()
