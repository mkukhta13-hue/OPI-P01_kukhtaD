"""Відкриті тести задачі 10: Дошка спринту та вигоряння.

Запуск: pytest tests/test_lab_10.py
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


T10 = [('S1',
  'board_summary',
  ([], ['Backlog', 'Todo', 'In progress', 'In review', 'Done']),
  {'counts': {'Backlog': 0, 'Todo': 0, 'In progress': 0, 'In review': 0, 'Done': 0},
   'points': {'Backlog': 0, 'Todo': 0, 'In progress': 0, 'In review': 0, 'Done': 0},
   'total_points': 0,
   'done_points': 0,
   'progress': 0.0,
   'wip_violations': [],
   'unassigned': []}),
 ('S1',
  'board_summary',
  ([{'id': 'c1', 'title': 'Задача c1', 'column': 'Todo', 'points': 3, 'assignee': 'ann'},
    {'id': 'c2', 'title': 'Задача c2', 'column': 'In progress', 'points': 5, 'assignee': 'bob'},
    {'id': 'c3', 'title': 'Задача c3', 'column': 'Done', 'points': 2, 'assignee': 'ann'},
    {'id': 'c4', 'title': 'Задача c4', 'column': 'Done', 'points': 3, 'assignee': 'bob'}],
   ['Backlog', 'Todo', 'In progress', 'In review', 'Done']),
  {'counts': {'Backlog': 0, 'Todo': 1, 'In progress': 1, 'In review': 0, 'Done': 2},
   'points': {'Backlog': 0, 'Todo': 3, 'In progress': 5, 'In review': 0, 'Done': 5},
   'total_points': 13,
   'done_points': 5,
   'progress': 38.5,
   'wip_violations': [],
   'unassigned': []}),
 ('S1',
  'board_summary',
  ([{'id': 'a', 'title': 'Задача a', 'column': 'Done', 'points': 2, 'assignee': 'ann'},
    {'id': 'b', 'title': 'Задача b', 'column': 'Done', 'points': 3, 'assignee': 'ann'}],
   ['Backlog', 'Todo', 'In progress', 'In review', 'Done']),
  {'counts': {'Backlog': 0, 'Todo': 0, 'In progress': 0, 'In review': 0, 'Done': 2},
   'points': {'Backlog': 0, 'Todo': 0, 'In progress': 0, 'In review': 0, 'Done': 5},
   'total_points': 5,
   'done_points': 5,
   'progress': 100.0,
   'wip_violations': [],
   'unassigned': []}),
 ('S2',
  'board_summary',
  ([{'id': 'a', 'title': 'Задача a', 'column': 'In progress', 'points': 1, 'assignee': 'ann'},
    {'id': 'b', 'title': 'Задача b', 'column': 'In progress', 'points': 1, 'assignee': 'ann'},
    {'id': 'c', 'title': 'Задача c', 'column': 'In progress', 'points': 1, 'assignee': 'ann'}],
   ['Backlog', 'Todo', 'In progress', 'In review', 'Done'],
   {'In progress': 2}),
  {'counts': {'Backlog': 0, 'Todo': 0, 'In progress': 3, 'In review': 0, 'Done': 0},
   'points': {'Backlog': 0, 'Todo': 0, 'In progress': 3, 'In review': 0, 'Done': 0},
   'total_points': 3,
   'done_points': 0,
   'progress': 0.0,
   'wip_violations': ['In progress'],
   'unassigned': []}),
 ('S2',
  'board_summary',
  ([{'id': 'a', 'title': 'Задача a', 'column': 'In progress', 'points': 1, 'assignee': 'ann'},
    {'id': 'b', 'title': 'Задача b', 'column': 'In progress', 'points': 1, 'assignee': 'ann'}],
   ['Backlog', 'Todo', 'In progress', 'In review', 'Done'],
   {'In progress': 2}),
  {'counts': {'Backlog': 0, 'Todo': 0, 'In progress': 2, 'In review': 0, 'Done': 0},
   'points': {'Backlog': 0, 'Todo': 0, 'In progress': 2, 'In review': 0, 'Done': 0},
   'total_points': 2,
   'done_points': 0,
   'progress': 0.0,
   'wip_violations': [],
   'unassigned': []}),
 ('S2',
  'board_summary',
  ([{'id': 'a', 'title': 'Задача a', 'column': 'In progress', 'points': 1, 'assignee': 'ann'},
    {'id': 'b', 'title': 'Задача b', 'column': 'In progress', 'points': 1, 'assignee': 'ann'},
    {'id': 'c', 'title': 'Задача c', 'column': 'In review', 'points': 1, 'assignee': 'ann'},
    {'id': 'd', 'title': 'Задача d', 'column': 'In review', 'points': 1, 'assignee': 'ann'}],
   ['Backlog', 'Todo', 'In progress', 'In review', 'Done'],
   {'In review': 1, 'In progress': 1}),
  {'counts': {'Backlog': 0, 'Todo': 0, 'In progress': 2, 'In review': 2, 'Done': 0},
   'points': {'Backlog': 0, 'Todo': 0, 'In progress': 2, 'In review': 2, 'Done': 0},
   'total_points': 4,
   'done_points': 0,
   'progress': 0.0,
   'wip_violations': ['In progress', 'In review'],
   'unassigned': []}),
 ('S3',
  'board_summary',
  ([{'id': 'c1', 'title': 'Задача c1', 'column': 'Todo', 'points': 1, 'assignee': 'ann'},
    {'id': 'c1', 'title': 'Задача c1', 'column': 'Done', 'points': 1, 'assignee': 'ann'}],
   ['Backlog', 'Todo', 'In progress', 'In review', 'Done']),
  ValueError('Дубль картки: c1')),
 ('S3',
  'board_summary',
  ([{'id': 'c1', 'title': 'Задача c1', 'column': 'Todo', 'points': 1, 'assignee': 'ann'},
    {'id': 'c2', 'title': 'Задача c2', 'column': 'Review', 'points': 1, 'assignee': 'ann'}],
   ['Backlog', 'Todo', 'In progress', 'In review', 'Done']),
  ValueError('Невідома колонка: Review (картка c2)')),
 ('S3',
  'board_summary',
  ([{'id': 'c1', 'title': 'Задача c1', 'column': 'Todo', 'points': 1, 'assignee': 'ann'},
    {'id': 'c3', 'title': 'Задача c3', 'column': 'Todo', 'points': -1, 'assignee': 'ann'}],
   ['Backlog', 'Todo', 'In progress', 'In review', 'Done']),
  ValueError('Некоректні очки: c3'))]


@pytest.mark.parametrize("tag,fn,args,expected", T10, ids=_ids(T10, "T10"))
def test_task_10(tag, fn, args, expected):
    run(10, fn, args, expected)
