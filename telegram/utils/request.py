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
"""This module contains methods to make POST and GET requests"""

import json
import socket
import logging

import certifi
import urllib3
from urllib3.connection import HTTPConnection

from telegram import (InputFile, TelegramError)
from telegram.error import Unauthorized, NetworkError, TimedOut, BadRequest

_CON_POOL = None
""":type: urllib3.PoolManager"""
CON_POOL_SIZE = 1

logging.getLogger('urllib3').setLevel(logging.WARNING)


def _get_con_pool():
    global _CON_POOL

    if _CON_POOL is not None:
        return _CON_POOL

    _CON_POOL = urllib3.PoolManager(maxsize=CON_POOL_SIZE,
                                    cert_reqs='CERT_REQUIRED',
                                    ca_certs=certifi.where(),
                                    socket_options=HTTPConnection.default_socket_options + [
                                        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                                    ])
    return _CON_POOL


def is_con_pool_initialized():
    return _CON_POOL is not None


def stop_con_pool():
    global _CON_POOL
    if _CON_POOL is not None:
        _CON_POOL.clear()
        _CON_POOL = None


def _parse(json_data):
    """Try and parse the JSON returned from Telegram.

    Returns:
        dict: A JSON parsed as Python dict with results - on error this dict will be empty.

    """
    decoded_s = json_data.decode('utf-8')
    try:
        data = json.loads(decoded_s)
    except ValueError:
        raise TelegramError('Invalid server response')

    if not data.get('ok') and data.get('description'):
        return data['description']

    return data['result']


def _request_wrapper(*args, **kwargs):
    """Wraps urllib3 request for handling known exceptions.

    Args:
        args: unnamed arguments, passed to urllib3 request.
        kwargs: keyword arguments, passed tp urllib3 request.

    Returns:
        str: A non-parsed JSON text.

    Raises:
        TelegramError

    """

    try:
        resp = _get_con_pool().request(*args, **kwargs)
    except urllib3.exceptions.TimeoutError as error:
        raise TimedOut()
    except urllib3.exceptions.HTTPError as error:
        # HTTPError must come last as its the base urllib3 exception class
        # TODO: do something smart here; for now just raise NetworkError
        raise NetworkError('urllib3 HTTPError {0}'.format(error))

    if 200 <= resp.status <= 299:
        # 200-299 range are HTTP success statuses
        return resp.data

    try:
        message = _parse(resp.data)
    except ValueError:
        raise NetworkError('Unknown HTTPError {0}'.format(resp.status))

    if resp.status in (401, 403):
        raise Unauthorized()
    elif resp.status == 400:
        raise BadRequest(repr(message))
    elif resp.status == 502:
        raise NetworkError('Bad Gateway')
    else:
        raise NetworkError('{0} ({1})'.format(message, resp.status))


def get(url):
    """Request an URL.
    Args:
      url:
        The web location we want to retrieve.

    Returns:
      A JSON object.

    """
    result = _request_wrapper('GET', url)

    return _parse(result)


def post(url, data, timeout=None):
    """Request an URL.
    Args:
      url:
        The web location we want to retrieve.
      data:
        A dict of (str, unicode) key/value pairs.
      timeout:
        float. If this value is specified, use it as the definitive timeout (in
        seconds) for urlopen() operations. [Optional]

    Notes:
      If neither `timeout` nor `data['timeout']` is specified. The underlying
      defaults are used.

    Returns:
      A JSON object.

    """
    urlopen_kwargs = {}

    if timeout is not None:
        urlopen_kwargs['timeout'] = timeout

    if InputFile.is_inputfile(data):
        data = InputFile(data)
        result = _request_wrapper('POST', url, body=data.to_form(), headers=data.headers)
    else:
        data = json.dumps(data)
        result = _request_wrapper('POST',
                                  url,
                                  body=data.encode(),
                                  headers={'Content-Type': 'application/json'})

    return _parse(result)


def download(url, filename):
    """Download a file by its URL.
    Args:
      url:
        The web location we want to retrieve.

      filename:
        The filename within the path to download the file.

    """
    buf = _request_wrapper('GET', url)
    with open(filename, 'wb') as fobj:
        fobj.write(buf)
