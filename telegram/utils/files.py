#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
"""This module contains helper functions related to handling of files.

.. versionchanged:: 14.0
   Previously, the contents of this module were available through the (no longer existing)
   module ``telegram.utils.helpers``.

Warning:
    Contents of this module are intended to be used internally by the library and *not* by the
    user. Changes to this module are not considered breaking changes and may not be documented in
    the changelog.
"""

from pathlib import Path
from typing import Optional, Union, Type, Any, cast, IO, TYPE_CHECKING

from telegram.utils.types import FileInput

if TYPE_CHECKING:
    from telegram import TelegramObject, InputFile


def is_local_file(obj: Optional[Union[str, Path]]) -> bool:
    """
    Checks if a given string is a file on local system.

    Args:
        obj (:obj:`str`): The string to check.
    """
    if obj is None:
        return False

    path = Path(obj)
    try:
        return path.is_file()
    except Exception:
        return False


def parse_file_input(
    file_input: Union[FileInput, 'TelegramObject'],
    tg_type: Type['TelegramObject'] = None,
    attach: bool = None,
    filename: str = None,
) -> Union[str, 'InputFile', Any]:
    """
    Parses input for sending files:

    * For string input, if the input is an absolute path of a local file,
      adds the ``file://`` prefix. If the input is a relative path of a local file, computes the
      absolute path and adds the ``file://`` prefix. Returns the input unchanged, otherwise.
    * :class:`pathlib.Path` objects are treated the same way as strings.
    * For IO and bytes input, returns an :class:`telegram.InputFile`.
    * If :attr:`tg_type` is specified and the input is of that type, returns the ``file_id``
      attribute.

    Args:
        file_input (:obj:`str` | :obj:`bytes` | `filelike object` | Telegram media object): The
            input to parse.
        tg_type (:obj:`type`, optional): The Telegram media type the input can be. E.g.
            :class:`telegram.Animation`.
        attach (:obj:`bool`, optional): Whether this file should be send as one file or is part of
            a collection of files. Only relevant in case an :class:`telegram.InputFile` is
            returned.
        filename (:obj:`str`, optional): The filename. Only relevant in case an
            :class:`telegram.InputFile` is returned.

    Returns:
        :obj:`str` | :class:`telegram.InputFile` | :obj:`object`: The parsed input or the untouched
        :attr:`file_input`, in case it's no valid file input.
    """
    # Importing on file-level yields cyclic Import Errors
    from telegram import InputFile  # pylint: disable=C0415

    if isinstance(file_input, str) and file_input.startswith('file://'):
        return file_input
    if isinstance(file_input, (str, Path)):
        if is_local_file(file_input):
            out = Path(file_input).absolute().as_uri()
        else:
            out = file_input  # type: ignore[assignment]
        return out
    if isinstance(file_input, bytes):
        return InputFile(file_input, attach=attach, filename=filename)
    if InputFile.is_file(file_input):
        file_input = cast(IO, file_input)
        return InputFile(file_input, attach=attach, filename=filename)
    if tg_type and isinstance(file_input, tg_type):
        return file_input.file_id  # type: ignore[attr-defined]
    return file_input
