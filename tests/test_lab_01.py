"""Відкриті тести задачі 1: Розбір назви гілки.

Запуск: pytest tests/test_lab_01.py
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import copy
import signal

import pytest
from conftest import load


def _same(a, b):
    """Рівність із допуском для дробових чисел; список і кортеж вважаються однаковими послідовностями."""
    if isinstance(a, float) or isinstance(b, float):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) < 1e-9
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    return a == b


def run(task, fn, args, expected):
    """Викликає функцію задачі на копії аргументів і порівнює результат; вхідні дані змінювати не можна."""
    func = getattr(load(task), fn)
    given = copy.deepcopy(args)
    if isinstance(expected, ValueError):
        with pytest.raises(ValueError) as info:
            func(*given)
        assert str(info.value) == str(expected)
    else:
        got = func(*given)
        assert _same(got, expected), f"отримано {got!r}, очікувалось {expected!r}"
    assert given == args, "функція не повинна змінювати вхідні дані"


def _ids(cases, prefix):
    return [f"{prefix}-{c[0]}-{i}" for i, c in enumerate(cases)]


@pytest.fixture(autouse=True)
def _watchdog():
    """Тест, що завис (нескінченний цикл), завершується за 10 с."""
    def boom(signum, frame):
        raise TimeoutError("тест завис довше 10 с: перевірте умови завершення циклів")
    old = signal.signal(signal.SIGALRM, boom)
    signal.alarm(10)
    yield
    signal.alarm(0)
    signal.signal(signal.SIGALRM, old)


T01 = [('S1',
  'parse_branch',
  ('feature/12-login-form', 'trunk'),
  {'kind': 'feature', 'issue': 12, 'slug': 'login-form', 'version': ''}),
 ('S1', 'parse_branch', ('main', 'trunk'), {'kind': 'main', 'issue': None, 'slug': '', 'version': ''}),
 ('S1',
  'parse_branch',
  ('fix/7-null-pointer', 'trunk'),
  {'kind': 'fix', 'issue': 7, 'slug': 'null-pointer', 'version': ''}),
 ('S2',
  'parse_branch',
  ('develop', 'gitflow'),
  {'kind': 'develop', 'issue': None, 'slug': '', 'version': ''}),
 ('S2', 'parse_branch', ('main', 'gitflow'), {'kind': 'main', 'issue': None, 'slug': '', 'version': ''}),
 ('S2',
  'parse_branch',
  ('feature/3-cart', 'gitflow'),
  {'kind': 'feature', 'issue': 3, 'slug': 'cart', 'version': ''}),
 ('S3', 'parse_branch', ('main', 'other'), ValueError('Невідома стратегія: other')),
 ('S3', 'parse_branch', ('', 'trunk'), ValueError('Порожня назва гілки')),
 ('S3', 'parse_branch', ('feature/1-a b', 'trunk'), ValueError('Назва гілки містить пробіли: feature/1-a b'))]


@pytest.mark.parametrize("tag,fn,args,expected", T01, ids=_ids(T01, "T01"))
def test_task_01(tag, fn, args, expected):
    run(1, fn, args, expected)
