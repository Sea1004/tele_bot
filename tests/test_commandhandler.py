#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
from queue import Queue

import pytest

from telegram import (Message, Update, Chat, Bot, User, CallbackQuery, InlineQuery,
                      ChosenInlineResult, ShippingQuery, PreCheckoutQuery)
from telegram.ext import CommandHandler, Filters, BaseFilter, CallbackContext, JobQueue

message = Message(1, User(1, '', False), None, Chat(1, ''), text='test')

params = [
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat', message=message)},
    {'channel_post': message},
    {'edited_channel_post': message},
    {'inline_query': InlineQuery(1, User(1, '', False), '', '')},
    {'chosen_inline_result': ChosenInlineResult('id', User(1, '', False), '')},
    {'shipping_query': ShippingQuery('id', User(1, '', False), '', None)},
    {'pre_checkout_query': PreCheckoutQuery('id', User(1, '', False), '', 0, '')},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat')}
]

ids = ('callback_query', 'channel_post', 'edited_channel_post', 'inline_query',
       'chosen_inline_result', 'shipping_query', 'pre_checkout_query',
       'callback_query_without_message',)


@pytest.fixture(scope='class', params=params, ids=ids)
def false_update(request):
    return Update(update_id=1, **request.param)


@pytest.fixture(scope='function')
def message(bot):
    return Message(1, User(1, '', False), None, Chat(1, ''), bot=bot)


class TestCommandHandler(object):
    test_flag = False

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def callback_basic(self, bot, update):
        test_bot = isinstance(bot, Bot)
        test_update = isinstance(update, Update)
        self.test_flag = test_bot and test_update

    def callback_data_1(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) or (chat_data is not None)

    def callback_data_2(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) and (chat_data is not None)

    def callback_queue_1(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) or (update_queue is not None)

    def callback_queue_2(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) and (update_queue is not None)

    def ch_callback_args(self, bot, update, args):
        if update.message.text == '/test':
            self.test_flag = len(args) == 0
        elif update.message.text == '/test@{}'.format(bot.username):
            self.test_flag = len(args) == 0
        else:
            self.test_flag = args == ['one', 'two']

    def callback_context(self, update, context):
        self.test_flag = (isinstance(context, CallbackContext) and
                          isinstance(context.bot, Bot) and
                          isinstance(update, Update) and
                          isinstance(context.update_queue, Queue) and
                          isinstance(context.job_queue, JobQueue) and
                          isinstance(context.user_data, dict) and
                          isinstance(context.chat_data, dict) and
                          isinstance(update.message, Message))

    def callback_context_args(self, update, context):
        self.test_flag = context.args == ['one', 'two']

    def test_basic(self, dp, message):
        handler = CommandHandler('test', self.callback_basic)
        dp.add_handler(handler)

        message.text = '/test'
        dp.process_update(Update(0, message))
        assert self.test_flag

        message.text = '/nottest'
        check = handler.check_update(Update(0, message))
        assert check is None or check is False

        message.text = 'test'
        check = handler.check_update(Update(0, message))
        assert check is None or check is False

        message.text = 'not /test at start'
        check = handler.check_update(Update(0, message))
        assert check is None or check is False

    def test_command_list(self, message):
        handler = CommandHandler(['test', 'start'], self.callback_basic)

        message.text = '/test'
        check = handler.check_update(Update(0, message))

        message.text = '/start'
        check = handler.check_update(Update(0, message))

        message.text = '/stop'
        check = handler.check_update(Update(0, message))
        assert check is None or check is False

    def test_edited(self, message):
        handler = CommandHandler('test', self.callback_basic,
                                 allow_edited=False)

        message.text = '/test'
        check = handler.check_update(Update(0, message))
        assert check is not None and check is not False
        check = handler.check_update(Update(0, edited_message=message))
        assert check is None or check is False
        handler.allow_edited = True
        check = handler.check_update(Update(0, message))
        assert check is not None and check is not False
        check = handler.check_update(Update(0, edited_message=message))
        assert check is not None and check is not False

    def test_directed_commands(self, message):
        handler = CommandHandler('test', self.callback_basic)

        message.text = '/test@{}'.format(message.bot.username)
        check = handler.check_update(Update(0, message))
        assert check is not None and check is not False

        message.text = '/test@otherbot'
        assert not handler.check_update(Update(0, message))

    def test_with_filter(self, message):
        handler = CommandHandler('test', self.callback_basic, Filters.group)

        message.chat = Chat(-23, 'group')
        message.text = '/test'
        check = handler.check_update(Update(0, message))
        assert check is not None and check is not False

        message.chat = Chat(23, 'private')
        check = handler.check_update(Update(0, message))
        assert check is None or check is False

    def test_pass_args(self, dp, message):
        handler = CommandHandler('test', self.ch_callback_args, pass_args=True)
        dp.add_handler(handler)

        message.text = '/test'
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        self.test_flag = False
        message.text = '/test@{}'.format(message.bot.username)
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        self.test_flag = False
        message.text = '/test one two'
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        self.test_flag = False
        message.text = '/test@{} one two'.format(message.bot.username)
        dp.process_update(Update(0, message=message))
        assert self.test_flag

    def test_newline(self, dp, message):
        handler = CommandHandler('test', self.callback_basic)
        dp.add_handler(handler)

        message.text = '/test\nfoobar'
        check = handler.check_update(Update(0, message))
        assert check is not None and check is not False
        dp.process_update(Update(0, message))
        assert self.test_flag

    def test_single_char(self, dp, message):
        # Regression test for https://github.com/python-telegram-bot/python-telegram-bot/issues/871
        handler = CommandHandler('test', self.callback_basic)
        dp.add_handler(handler)

        message.text = 'a'
        check = handler.check_update(Update(0, message))
        assert check is None or check is False

    def test_single_slash(self, dp, message):
        # Regression test for https://github.com/python-telegram-bot/python-telegram-bot/issues/871
        handler = CommandHandler('test', self.callback_basic)
        dp.add_handler(handler)

        message.text = '/'
        check = handler.check_update(Update(0, message))
        assert check is None or check is False

        message.text = '/ test'
        check = handler.check_update(Update(0, message))
        assert check is None or check is False

    def test_pass_user_or_chat_data(self, dp, message):
        handler = CommandHandler('test', self.callback_data_1,
                                 pass_user_data=True)
        dp.add_handler(handler)

        message.text = '/test'
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CommandHandler('test', self.callback_data_1,
                                 pass_chat_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CommandHandler('test', self.callback_data_2,
                                 pass_chat_data=True,
                                 pass_user_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag

    def test_pass_job_or_update_queue(self, dp, message):
        handler = CommandHandler('test', self.callback_queue_1,
                                 pass_job_queue=True)
        dp.add_handler(handler)

        message.text = '/test'
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CommandHandler('test', self.callback_queue_1,
                                 pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CommandHandler('test', self.callback_queue_2,
                                 pass_job_queue=True,
                                 pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(Update(0, message=message))
        assert self.test_flag

    def test_other_update_types(self, false_update):
        handler = CommandHandler('test', self.callback_basic)
        check = handler.check_update(false_update)
        assert check is None or check is False

    def test_filters_for_wrong_command(self, message):
        """Filters should not be executed if the command does not match the handler"""

        class TestFilter(BaseFilter):
            def __init__(self):
                self.tested = False

            def filter(self, message):
                self.tested = True

        test_filter = TestFilter()

        handler = CommandHandler('foo', self.callback_basic,
                                 filters=test_filter)
        message.text = '/bar'

        check = handler.check_update(Update(0, message=message))
        assert check is None or check is False

        assert not test_filter.tested

    def test_context(self, cdp, message):
        handler = CommandHandler('test', self.callback_context)
        cdp.add_handler(handler)

        message.text = '/test'
        cdp.process_update(Update(0, message))
        assert self.test_flag

    def test_context_args(self, cdp, message):
        handler = CommandHandler('test', self.callback_context_args)
        cdp.add_handler(handler)

        message.text = '/test'
        cdp.process_update(Update(0, message))
        assert not self.test_flag

        message.text = '/test one two'
        cdp.process_update(Update(0, message))
        assert self.test_flag
