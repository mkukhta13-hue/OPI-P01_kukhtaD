"""Відкриті тести задачі 9: Готовність pull request до злиття.

Запуск: pytest tests/test_lab_09.py
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


T09 = [('S1',
  'can_merge',
  ({'author': 'ann',
    'draft': False,
    'mergeable': True,
    'up_to_date': True,
    'reviews': [{'user': 'bob', 'state': 'APPROVED'}],
    'checks': {'tests': 'success'},
    'labels': []},
   {'approvals': 1, 'checks': ['tests']}),
  {'ok': True, 'reasons': []}),
 ('S1',
  'can_merge',
  ({'author': 'ann',
    'draft': True,
    'mergeable': True,
    'up_to_date': True,
    'reviews': [{'user': 'bob', 'state': 'APPROVED'}],
    'checks': {'tests': 'success'},
    'labels': []},
   {'approvals': 1, 'checks': ['tests']}),
  {'ok': False, 'reasons': ['Чернетка']}),
 ('S1',
  'can_merge',
  ({'author': 'ann',
    'draft': False,
    'mergeable': False,
    'up_to_date': True,
    'reviews': [{'user': 'bob', 'state': 'APPROVED'}],
    'checks': {'tests': 'success'},
    'labels': []},
   {'approvals': 1, 'checks': ['tests']}),
  {'ok': False, 'reasons': ['Є конфлікти']}),
 ('S2',
  'can_merge',
  ({'author': 'ann',
    'draft': False,
    'mergeable': True,
    'up_to_date': True,
    'reviews': [{'user': 'ann', 'state': 'APPROVED'}],
    'checks': {'tests': 'success'},
    'labels': []},
   {'approvals': 1, 'checks': ['tests']}),
  {'ok': False, 'reasons': ['Недостатньо схвалень: 0 з 1']}),
 ('S2',
  'can_merge',
  ({'author': 'ann',
    'draft': False,
    'mergeable': True,
    'up_to_date': True,
    'reviews': [{'user': 'ann', 'state': 'APPROVED'}],
    'checks': {'tests': 'success'},
    'labels': []},
   {'approvals': 1, 'checks': ['tests'], 'self_approval': True}),
  {'ok': True, 'reasons': []}),
 ('S2',
  'can_merge',
  ({'author': 'ann',
    'draft': False,
    'mergeable': True,
    'up_to_date': True,
    'reviews': [{'user': 'bob', 'state': 'APPROVED'}, {'user': 'bob', 'state': 'APPROVED'}],
    'checks': {'tests': 'success'},
    'labels': []},
   {'approvals': 2, 'checks': ['tests']}),
  {'ok': False, 'reasons': ['Недостатньо схвалень: 1 з 2']}),
 ('S3',
  'can_merge',
  ({'author': 'ann',
    'draft': False,
    'mergeable': True,
    'up_to_date': False,
    'reviews': [{'user': 'bob', 'state': 'APPROVED'}],
    'checks': {'tests': 'success'},
    'labels': []},
   {'approvals': 1, 'checks': ['tests'], 'up_to_date': True}),
  {'ok': False, 'reasons': ['Гілка відстає від main']}),
 ('S3',
  'can_merge',
  ({'author': 'ann',
    'draft': False,
    'mergeable': True,
    'up_to_date': False,
    'reviews': [{'user': 'bob', 'state': 'APPROVED'}],
    'checks': {'tests': 'success'},
    'labels': []},
   {'approvals': 1, 'checks': ['tests']}),
  {'ok': True, 'reasons': []}),
 ('S3',
  'can_merge',
  ({'author': 'ann',
    'draft': False,
    'mergeable': True,
    'up_to_date': True,
    'reviews': [{'user': 'bob', 'state': 'APPROVED'}],
    'checks': {'tests': 'success'},
    'labels': ['wip', 'bug']},
   {'approvals': 1, 'blocking_labels': ['wip', 'do-not-merge']}),
  {'ok': False, 'reasons': ['Заборонена мітка: wip']})]


@pytest.mark.parametrize("tag,fn,args,expected", T09, ids=_ids(T09, "T09"))
def test_task_09(tag, fn, args, expected):
    run(9, fn, args, expected)
