#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# File   : kv_session.py
# Author : Jiayuan Mao
# Email  : maojiayuan@gmail.com
# Date   : 10/23/2018
#
# This file is part of Jacinle.
# Distributed under terms of the MIT license.

import collections

from jacinle.storage.kv.kv import KVStoreBase
from jacinle.storage.kv.mem import MemKVStore
from jacinle.storage.kv.memcached import MemcachedKVStore
from .session import SessionManagerBase

__all__ = [
    'SessionIdentifier',
    'KVBasedSessionManager',
    'InMemorySessionManager',
    'MemcachedSessionManager'
]


class SessionIdentifier(collections.namedtuple('SessionIdentifier', ['session_id', 'hmac_key'])):
    session_id: str
    hmac_key: str


class KVBasedSessionManager(SessionManagerBase):
    def __init__(self, secret: str, kvstore: KVStoreBase, timeout: int, cookie_prefix: str = 'jac_ses_', kv_prefix: str = 'jac_ses_'):
        super().__init__(secret)

        self.kvstore = kvstore
        self.cookie_prefix = cookie_prefix
        self.kv_prefix = kv_prefix
        self.session_timeout = timeout

    def get(self, request_handler):
        session_id = hmac_key = None
        if request_handler is not None:
            session_id = request_handler.get_secure_cookie(self.cookie_prefix + 'session_id')
            if session_id is not None:
                session_id = session_id.decode('utf8')
            hmac_key = request_handler.get_secure_cookie(self.cookie_prefix + 'verification')
            if hmac_key is not None:
                hmac_key = hmac_key.decode('utf8')

        if session_id is None:
            session_exists = False
            session_id = self._generate_id()
            hmac_key = self._generate_hmac(session_id)
        else:
            session_exists = True

        data = {}
        if session_exists and hmac_key == self._generate_hmac(session_id):
            data = self._get_from_kvstore(self.kv_prefix + session_id, data, timeout=self.session_timeout)
        return SessionIdentifier(session_id, hmac_key), data

    def set(self, request_handler, identifier, data):
        request_handler.set_secure_cookie(self.cookie_prefix + 'session_id', identifier.session_id.encode('utf8'))
        request_handler.set_secure_cookie(self.cookie_prefix + 'verification', identifier.hmac_key.encode('utf8'))
        self._put_to_kvstore(self.kv_prefix + identifier.session_id, data, timeout=self.session_timeout)

    def _get_from_kvstore(self, key, default, timeout):
        raise NotImplementedError()

    def _put_to_kvstore(self, key, value, timeout):
        raise NotImplementedError()


class InMemorySessionManager(KVBasedSessionManager):
    def __init__(self, secret: str, timeout: int, cookie_prefix: str = 'jac_ses_', kv_prefix: str = 'jac_ses_'):
        super().__init__(secret, MemKVStore(), timeout, cookie_prefix, kv_prefix)

    def _get_from_kvstore(self, key, default, timeout):
        data, _ = self.kvstore.get(key, (None, 0))
        if data is None:
            data = default
        self.kvstore.put(key, (data, timeout))
        return data

    def _put_to_kvstore(self, key, value, timeout):
        self.kvstore.put(key, (value, timeout))


class MemcachedSessionManager(KVBasedSessionManager):
    def __init__(self, secret, memcache_host, memcache_port, timeout, cookie_prefix='jac_ses_', kv_prefix='jac_ses_'):
        kvstore = MemcachedKVStore(memcache_host, memcache_port)
        assert kvstore.available
        super().__init__(secret, kvstore, timeout, cookie_prefix, kv_prefix)

    def _get_from_kvstore(self, key, default, timeout):
        return self.memcache.get(key, default, refresh=True, refresh_timeout=timeout)

    def _put_to_kvstore(self, key, value, timeout):
        self.memcache.put(key, value, replace=True, timeout=timeout)

