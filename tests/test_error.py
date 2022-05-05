#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
import pickle
from collections import defaultdict

import pytest

from telegram.error import (
    BadRequest,
    ChatMigrated,
    Conflict,
    Forbidden,
    InvalidToken,
    NetworkError,
    PassportDecryptionError,
    RetryAfter,
    TelegramError,
    TimedOut,
)
from telegram.ext import InvalidCallbackData


class TestErrors:
    def test_telegram_error(self):
        with pytest.raises(TelegramError, match="^test message$"):
            raise TelegramError("test message")
        with pytest.raises(TelegramError, match="^Test message$"):
            raise TelegramError("Error: test message")
        with pytest.raises(TelegramError, match="^Test message$"):
            raise TelegramError("[Error]: test message")
        with pytest.raises(TelegramError, match="^Test message$"):
            raise TelegramError("Bad Request: test message")

    def test_unauthorized(self):
        with pytest.raises(Forbidden, match="test message"):
            raise Forbidden("test message")
        with pytest.raises(Forbidden, match="^Test message$"):
            raise Forbidden("Error: test message")
        with pytest.raises(Forbidden, match="^Test message$"):
            raise Forbidden("[Error]: test message")
        with pytest.raises(Forbidden, match="^Test message$"):
            raise Forbidden("Bad Request: test message")

    def test_invalid_token(self):
        with pytest.raises(InvalidToken, match="Invalid token"):
            raise InvalidToken

    def test_network_error(self):
        with pytest.raises(NetworkError, match="test message"):
            raise NetworkError("test message")
        with pytest.raises(NetworkError, match="^Test message$"):
            raise NetworkError("Error: test message")
        with pytest.raises(NetworkError, match="^Test message$"):
            raise NetworkError("[Error]: test message")
        with pytest.raises(NetworkError, match="^Test message$"):
            raise NetworkError("Bad Request: test message")

    def test_bad_request(self):
        with pytest.raises(BadRequest, match="test message"):
            raise BadRequest("test message")
        with pytest.raises(BadRequest, match="^Test message$"):
            raise BadRequest("Error: test message")
        with pytest.raises(BadRequest, match="^Test message$"):
            raise BadRequest("[Error]: test message")
        with pytest.raises(BadRequest, match="^Test message$"):
            raise BadRequest("Bad Request: test message")

    def test_timed_out(self):
        with pytest.raises(TimedOut, match="^Timed out$"):
            raise TimedOut

    def test_chat_migrated(self):
        with pytest.raises(ChatMigrated, match="Group migrated to supergroup. New chat id: 1234"):
            raise ChatMigrated(1234)
        try:
            raise ChatMigrated(1234)
        except ChatMigrated as e:
            assert e.new_chat_id == 1234

    def test_retry_after(self):
        with pytest.raises(RetryAfter, match="Flood control exceeded. Retry in 12.0 seconds"):
            raise RetryAfter(12)

    def test_conflict(self):
        with pytest.raises(Conflict, match="Something something."):
            raise Conflict("Something something.")

    @pytest.mark.parametrize(
        "exception, attributes",
        [
            (TelegramError("test message"), ["message"]),
            (Forbidden("test message"), ["message"]),
            (InvalidToken(), ["message"]),
            (NetworkError("test message"), ["message"]),
            (BadRequest("test message"), ["message"]),
            (TimedOut(), ["message"]),
            (ChatMigrated(1234), ["message", "new_chat_id"]),
            (RetryAfter(12), ["message", "retry_after"]),
            (Conflict("test message"), ["message"]),
            (PassportDecryptionError("test message"), ["message"]),
            (InvalidCallbackData("test data"), ["callback_data"]),
        ],
    )
    def test_errors_pickling(self, exception, attributes):
        pickled = pickle.dumps(exception)
        unpickled = pickle.loads(pickled)
        assert type(unpickled) is type(exception)
        assert str(unpickled) == str(exception)

        for attribute in attributes:
            assert getattr(unpickled, attribute) == getattr(exception, attribute)

    @pytest.mark.parametrize(
        "inst",
        [
            (TelegramError("test message")),
            (Forbidden("test message")),
            (InvalidToken()),
            (NetworkError("test message")),
            (BadRequest("test message")),
            (TimedOut()),
            (ChatMigrated(1234)),
            (RetryAfter(12)),
            (Conflict("test message")),
            (PassportDecryptionError("test message")),
            (InvalidCallbackData("test data")),
        ],
    )
    def test_slot_behaviour(self, inst, mro_slots):
        for attr in inst.__slots__:
            assert getattr(inst, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    def test_coverage(self):
        """
        This test is only here to make sure that new errors will override __reduce__ and set
        __slots__ properly.
        Add the new error class to the below covered_subclasses dict, if it's covered in the above
        test_errors_pickling and test_slots_behavior tests.
        """

        def make_assertion(cls):
            assert set(cls.__subclasses__()) == covered_subclasses[cls]
            for subcls in cls.__subclasses__():
                make_assertion(subcls)

        covered_subclasses = defaultdict(set)
        covered_subclasses.update(
            {
                TelegramError: {
                    Forbidden,
                    InvalidToken,
                    NetworkError,
                    ChatMigrated,
                    RetryAfter,
                    Conflict,
                    PassportDecryptionError,
                    InvalidCallbackData,
                },
                NetworkError: {BadRequest, TimedOut},
            }
        )

        make_assertion(TelegramError)

    def test_string_representations(self):
        """We just randomly test a few of the subclasses - should suffice"""
        e = TelegramError("This is a message")
        assert repr(e) == "TelegramError('This is a message')"
        assert str(e) == "This is a message"

        e = RetryAfter(42)
        assert repr(e) == "RetryAfter('Flood control exceeded. Retry in 42.0 seconds')"
        assert str(e) == "Flood control exceeded. Retry in 42.0 seconds"

        e = BadRequest("This is a message")
        assert repr(e) == "BadRequest('This is a message')"
        assert str(e) == "This is a message"
