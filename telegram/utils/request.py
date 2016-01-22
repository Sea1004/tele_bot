#!/usr/bin/env python
# pylint: disable=no-name-in-module,unused-import
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

"""This module contains methods to make POST and GET requests"""

import functools
import json
import socket
from ssl import SSLError

try:
    # python2
    from httplib import HTTPException
except ImportError:
    # python3
    from http.client import HTTPException

try:
    from urllib.request import urlopen, urlretrieve, Request
    from urllib.error import HTTPError
except ImportError:
    from urllib import urlretrieve
    from urllib2 import urlopen, Request
    from urllib2 import HTTPError

from telegram import (InputFile, TelegramError)


def _parse(json_data):
    """Try and parse the JSON returned from Telegram and return an empty
    dictionary if there is any error.

    Args:
      url:
        urllib.urlopen object

    Returns:
      A JSON parsed as Python dict with results.
    """
    decoded_s = json_data.decode('utf-8')
    try:
        data = json.loads(decoded_s)
    except ValueError:
        raise TelegramError('Invalid server response')

    if not data.get('ok') and data.get('description'):
        return data['description']

    return data['result']


def _try_except_req(func):
    """Decorator for requests to handle known exceptions"""
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as error:
            if error.getcode() == 403:
                raise TelegramError('Unauthorized')
            if error.getcode() == 502:
                raise TelegramError('Bad Gateway')

            try:
                message = _parse(error.read())
            except ValueError:
                message = 'Unknown HTTPError {0}'.format(error.getcode())

            raise TelegramError(message)
        except (SSLError, socket.timeout) as error:
            if "operation timed out" in str(error):
                raise TelegramError("Timed out")

            raise TelegramError(str(error))
        except HTTPException as error:
            raise TelegramError('HTTPException: {0!r}'.format(error))

    return decorator


@_try_except_req
def get(url):
    """Request an URL.
    Args:
      url:
        The web location we want to retrieve.

    Returns:
      A JSON object.
    """
    result = urlopen(url).read()

    return _parse(result)


@_try_except_req
def post(url,
         data,
         network_delay=2.):
    """Request an URL.
    Args:
      url:
        The web location we want to retrieve.
      data:
        A dict of (str, unicode) key/value pairs.
      network_delay:
        Additional timeout in seconds to allow the response from Telegram to
        take some time.

    Returns:
      A JSON object.
    """

    # Add time to the timeout of urlopen to allow data to be transferred over
    # the network.
    if 'timeout' in data:
        timeout = data['timeout'] + network_delay
    else:
        timeout = None

    if InputFile.is_inputfile(data):
        data = InputFile(data)
        request = Request(url,
                          data=data.to_form(),
                          headers=data.headers)
    else:
        data = json.dumps(data)
        request = Request(url,
                          data=data.encode(),
                          headers={'Content-Type': 'application/json'})

    result = urlopen(request, timeout=timeout).read()
    return _parse(result)


@_try_except_req
def download(url,
             filename):
    """Download a file by its URL.
    Args:
      url:
        The web location we want to retrieve.

      filename:
        The filename wihtin the path to download the file.
    """

    urlretrieve(url, filename)
