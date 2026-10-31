"""Відкриті тести задачі 4: Пошук блоків конфлікту.

Запуск: pytest tests/test_lab_04.py
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


T04 = [('S1', 'find_conflicts', ('a\nb',), []),
 ('S1', 'find_conflicts', ('',), []),
 ('S1',
  'find_conflicts',
  ('<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> feature/1-a',),
  [{'start': 1,
    'end': 5,
    'ours': ['x'],
    'base': None,
    'theirs': ['y'],
    'ours_label': 'HEAD',
    'theirs_label': 'feature/1-a'}]),
 ('S2',
  'find_conflicts',
  ('<<<<<<< ours\nA\n||||||| base\nB\n=======\nC\n>>>>>>> theirs',),
  [{'start': 1,
    'end': 7,
    'ours': ['A'],
    'base': ['B'],
    'theirs': ['C'],
    'ours_label': 'ours',
    'theirs_label': 'theirs'}]),
 ('S2',
  'find_conflicts',
  ('<<<<<<< a\n=======\nz\n>>>>>>> b',),
  [{'start': 1,
    'end': 4,
    'ours': [],
    'base': None,
    'theirs': ['z'],
    'ours_label': 'a',
    'theirs_label': 'b'}]),
 ('S2',
  'find_conflicts',
  ('<<<<<<< a\nz\n=======\n>>>>>>> b',),
  [{'start': 1,
    'end': 4,
    'ours': ['z'],
    'base': None,
    'theirs': [],
    'ours_label': 'a',
    'theirs_label': 'b'}]),
 ('S3', 'find_conflicts', ('=======\nx',), ValueError('Маркер без початку на рядку 1')),
 ('S3', 'find_conflicts', ('a\n>>>>>>> x',), ValueError('Маркер без початку на рядку 2')),
 ('S3', 'find_conflicts', ('a\n||||||| base',), ValueError('Маркер без початку на рядку 2'))]


@pytest.mark.parametrize("tag,fn,args,expected", T04, ids=_ids(T04, "T04"))
def test_task_04(tag, fn, args, expected):
    run(4, fn, args, expected)
