# -*- coding: utf-8 -*-
# File   : meta.py
# Author : Jiayuan Mao
# Email  : maojiayuan@gmail.com
# Date   : 1/18/18
#
# This file is part of Jacinle.

import functools
import collections
import threading
import contextlib

__all__ = [
    'gofor',
    'run_once', 'try_run',
    'map_exec', 'filter_exec',
    'cond_with',
    'merge_iterable',
    'dict_deep_update', 'dict_deep_keys',
    'assert_instance', 'assert_none', 'assert_notnone',
    'notnone_property',
    'synchronized'
]


def gofor(v):
    if isinstance(v, collections.Mapping):
        return v.items()
    assert_instance(v, collections.Iterable)
    return enumerate(v)


def run_once(func):
    has_run = False

    @synchronized()
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        nonlocal has_run
        if not has_run:
            has_run = True
            return func(*args, **kwargs)
        else:
            return
    return new_func


def try_run(lambda_):
    try:
        return lambda_()
    except Exception:
        return None


def map_exec(func, *iterables):
    return list(map(func, *iterables))


def filter_exec(func, iterable):
    return list(filter(func, iterable))


def method2func(method_name):
    return lambda x: getattr(x, method_name)()


@contextlib.contextmanager
def cond_with(with_statement, cond):
    if cond:
        with with_statement:
            yield
    else:
        yield


def merge_iterable(v1, v2):
    assert issubclass(type(v1), type(v2)) or issubclass(type(v2), type(v1))
    if isinstance(v1, (dict, set)):
        v = v1.copy().update(v2)
        return v

    return v1 + v2


def dict_deep_update(a, b):
    for key in b:
        if key in a and type(b[key]) is dict:
            dict_deep_update(a[key], b[key])
        else:
            a[key] = b[key]


def dict_deep_keys(d, sort=True, sep='.'):
    assert type(d) is dict

    def _dfs(current, result, prefix=None):
        for key in current:
            current_key = key if prefix is None else '{}{}{}'.format(prefix, sep, key)
            result.append(current_key)
            if type(current[key]) is dict:
                _dfs(current[key], res, current_key)

    res = list()
    _dfs(d, res)
    if sort:
        res.sort()
    return res


def assert_instance(ins, clz, msg=None):
    msg = msg or '{} (of type{}) is not of type {}'.format(ins, type(ins), clz)
    assert isinstance(ins, clz), msg


def assert_none(ins, msg=None):
    msg = msg or '{} is not None'.format(ins)
    assert ins is None, msg


def assert_notnone(ins, msg=None, name='instance'):
    msg = msg or '{} is None'.format(name)
    assert ins is not None, msg


class notnone_property:
    def __init__(self, fget):
        self.fget = fget
        self.__module__ = fget.__module__
        self.__name__ = fget.__name__
        self.__doc__ = fget.__doc__
        self.__prop_key  = '{}_{}'.format(
            fget.__name__, id(fget))

    def __get__(self, instance, owner):
        if instance is None:
            return self.fget
        v = self.fget(instance)
        assert v is not None, '{}.{} can not be None, maybe not set yet'.format(
                type(instance).__name__, self.__name__)
        return v


def synchronized(mutex=None):
    if mutex is None:
        mutex = threading.Lock()

    def wrapper(func):
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            with mutex:
                return func(*args, **kwargs)
        return wrapped_func

    return wrapper
