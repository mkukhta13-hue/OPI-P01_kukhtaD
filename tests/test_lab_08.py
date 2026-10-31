"""Відкриті тести задачі 8: Автоматичні зауваження до diff.

Запуск: pytest tests/test_lab_08.py
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


T08 = [('S1', 'lint_diff', ('',), []),
 ('S1',
  'lint_diff',
  ('diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1,2 +1,3 @@\n a = 1\n+# TODO: fix\n b = 2\n',),
  [{'path': 'x.py', 'line': 2, 'code': 'R001'}]),
 ('S1',
  'lint_diff',
  ('diff --git a/app.js b/app.js\n--- a/app.js\n+++ b/app.js\n@@ -0,0 +1,1 @@\n+// FIXME later\n',),
  [{'path': 'app.js', 'line': 1, 'code': 'R001'}]),
 ('S2',
  'lint_diff',
  ('diff --git a/x.py b/x.py\n'
   '--- a/x.py\n'
   '+++ b/x.py\n'
   '@@ -1,1 +1,2 @@\n'
   ' a\n'
   '+xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n',),
  [{'path': 'x.py', 'line': 2, 'code': 'R004'}]),
 ('S2',
  'lint_diff',
  ('diff --git a/x.py b/x.py\n'
   '--- a/x.py\n'
   '+++ b/x.py\n'
   '@@ -1,1 +1,2 @@\n'
   ' a\n'
   '+xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n',),
  []),
 ('S2',
  'lint_diff',
  ('diff --git a/c.py b/c.py\n--- a/c.py\n+++ b/c.py\n@@ -1,1 +1,2 @@\n a\n+password = "abc"\n',),
  [{'path': 'c.py', 'line': 2, 'code': 'R005'}]),
 ('S3',
  'lint_diff',
  ('diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1,1 +1,3 @@\n a\n+# TODO a\n+print(1) \n',
   {'R001'}),
  [{'path': 'x.py', 'line': 2, 'code': 'R001'}]),
 ('S3',
  'lint_diff',
  ('diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1,1 +1,3 @@\n a\n+# TODO a\n+print(1) \n',
   {'R001', 'R003'}),
  [{'path': 'x.py', 'line': 2, 'code': 'R001'}, {'path': 'x.py', 'line': 3, 'code': 'R003'}]),
 ('S3',
  'lint_diff',
  ('diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1,1 +1,2 @@\n a\n+# TODO a\n', set()),
  [])]


@pytest.mark.parametrize("tag,fn,args,expected", T08, ids=_ids(T08, "T08"))
def test_task_08(tag, fn, args, expected):
    run(8, fn, args, expected)
