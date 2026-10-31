"""Відкриті тести задачі 2: Розбір повідомлення коміту.

Запуск: pytest tests/test_lab_02.py
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


T02 = [('S1',
  'parse_commit',
  ('feat: add login',),
  {'type': 'feat', 'scope': None, 'breaking': False, 'subject': 'add login', 'body': '', 'footers': []}),
 ('S1',
  'parse_commit',
  ('fix(api): handle empty list',),
  {'type': 'fix',
   'scope': 'api',
   'breaking': False,
   'subject': 'handle empty list',
   'body': '',
   'footers': []}),
 ('S1',
  'parse_commit',
  ('feat(ui)!: drop old theme',),
  {'type': 'feat', 'scope': 'ui', 'breaking': True, 'subject': 'drop old theme', 'body': '', 'footers': []}),
 ('S2',
  'parse_commit',
  ('feat: add search\n\nAdds search by title.\n',),
  {'type': 'feat',
   'scope': None,
   'breaking': False,
   'subject': 'add search',
   'body': 'Adds search by title.',
   'footers': []}),
 ('S2',
  'parse_commit',
  ('fix: x\n\nCloses #12',),
  {'type': 'fix',
   'scope': None,
   'breaking': False,
   'subject': 'x',
   'body': '',
   'footers': [('Closes', '#12')]}),
 ('S2',
  'parse_commit',
  ('feat: a\n\nbody one\n\nbody two\n\nReviewed-by: Ірина\nRefs #7',),
  {'type': 'feat',
   'scope': None,
   'breaking': False,
   'subject': 'a',
   'body': 'body one\n\nbody two',
   'footers': [('Reviewed-by', 'Ірина'), ('Refs', '#7')]}),
 ('S3', 'parse_commit', ('',), ValueError('Порожнє повідомлення коміту')),
 ('S3', 'parse_commit', ('  \n ',), ValueError('Порожнє повідомлення коміту')),
 ('S3', 'parse_commit', ('add login',), ValueError('Заголовок не відповідає формату: add login'))]


@pytest.mark.parametrize("tag,fn,args,expected", T02, ids=_ids(T02, "T02"))
def test_task_02(tag, fn, args, expected):
    run(2, fn, args, expected)
