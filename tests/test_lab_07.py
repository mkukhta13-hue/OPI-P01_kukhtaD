"""Відкриті тести задачі 7: Статистика змін у diff.

Запуск: pytest tests/test_lab_07.py
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


T07 = [('S1', 'parse_diff', ('',), []),
 ('S1',
  'parse_diff',
  ('diff --git a/app.py b/app.py\n'
   'index 1111111..2222222 100644\n'
   '--- a/app.py\n'
   '+++ b/app.py\n'
   '@@ -1,3 +1,4 @@\n'
   ' import os\n'
   '+import sys\n'
   ' \n'
   ' def main():\n',),
  [{'path': 'app.py', 'old_path': 'app.py', 'status': 'modified', 'added': 1, 'removed': 0, 'hunks': 1}]),
 ('S1',
  'parse_diff',
  ('diff --git a/a.py b/a.py\n'
   'index 1111111..2222222 100644\n'
   '--- a/a.py\n'
   '+++ b/a.py\n'
   '@@ -1,2 +1,2 @@\n'
   ' a\n'
   '-b\n'
   '+c\n',),
  [{'path': 'a.py', 'old_path': 'a.py', 'status': 'modified', 'added': 1, 'removed': 1, 'hunks': 1}]),
 ('S2',
  'parse_diff',
  ('diff --git a/n.py b/n.py\n'
   'new file mode 100644\n'
   'index 0000000..3333333\n'
   '--- /dev/null\n'
   '+++ b/n.py\n'
   '@@ -0,0 +1,2 @@\n'
   '+x = 1\n'
   '+y = 2\n',),
  [{'path': 'n.py', 'old_path': 'n.py', 'status': 'added', 'added': 2, 'removed': 0, 'hunks': 1}]),
 ('S2',
  'parse_diff',
  ('diff --git a/gone.py b/gone.py\n'
   'deleted file mode 100644\n'
   'index 3333333..0000000\n'
   '--- a/gone.py\n'
   '+++ /dev/null\n'
   '@@ -1,2 +0,0 @@\n'
   '-x = 1\n'
   '-y = 2\n',),
  [{'path': 'gone.py', 'old_path': 'gone.py', 'status': 'deleted', 'added': 0, 'removed': 2, 'hunks': 1}]),
 ('S2',
  'parse_diff',
  ('diff --git a/old.py b/new.py\nsimilarity index 100%\nrename from old.py\nrename to new.py\n',),
  [{'path': 'new.py', 'old_path': 'old.py', 'status': 'renamed', 'added': 0, 'removed': 0, 'hunks': 0}]),
 ('S3',
  'parse_diff',
  ('diff --git a/a.txt b/a.txt\n'
   'index 1111111..2222222 100644\n'
   '--- a/a.txt\n'
   '+++ b/a.txt\n'
   '@@ -1 +1 @@\n'
   '-a\n'
   '+b\n',),
  [{'path': 'a.txt', 'old_path': 'a.txt', 'status': 'modified', 'added': 1, 'removed': 1, 'hunks': 1}]),
 ('S3',
  'parse_diff',
  ('diff --git a/a.md b/a.md\n'
   'index 1111111..2222222 100644\n'
   '--- a/a.md\n'
   '+++ b/a.md\n'
   '@@ -1,3 +1,3 @@\n'
   '--- old line\n'
   '-text\n'
   '+++ new line\n'
   '+text2\n'
   ' ctx\n',),
  [{'path': 'a.md', 'old_path': 'a.md', 'status': 'modified', 'added': 2, 'removed': 2, 'hunks': 1}]),
 ('S3',
  'parse_diff',
  ('diff --git a/a.md b/a.md\n'
   'index 1111111..2222222 100644\n'
   '--- a/a.md\n'
   '+++ b/a.md\n'
   '@@ -1,1 +1,1 @@\n'
   '--- old line\n'
   '+++ new line\n',),
  [{'path': 'a.md', 'old_path': 'a.md', 'status': 'modified', 'added': 1, 'removed': 1, 'hunks': 1}])]


@pytest.mark.parametrize("tag,fn,args,expected", T07, ids=_ids(T07, "T07"))
def test_task_07(tag, fn, args, expected):
    run(7, fn, args, expected)
