"""Відкриті тести задачі 6: Перевірка опису pull request.

Запуск: pytest tests/test_lab_06.py
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


T06 = [('S1',
  'check_pr_description',
  ('## Опис\n'
   'Додає пошук за назвою\n'
   '\n'
   '## Як перевірити\n'
   'Запустити pytest і відкрити сторінку\n'
   '\n'
   '## Чекліст\n'
   '- [x] Тести додано\n'
   '- [x] Документацію оновлено\n',
   ['Опис', 'Як перевірити', 'Чекліст'],
   None),
  []),
 ('S1',
  'check_pr_description',
  ('', ['Опис', 'Як перевірити'], None),
  ['Немає розділу: Опис', 'Немає розділу: Як перевірити']),
 ('S1',
  'check_pr_description',
  ('## Опис\nДодає пошук за назвою\n', ['Опис', 'Як перевірити'], None),
  ['Немає розділу: Як перевірити']),
 ('S2',
  'check_pr_description',
  ('## Опис\n'
   'Додає пошук за назвою\n'
   '\n'
   '## Як перевірити\n'
   'Запустити pytest і відкрити сторінку\n'
   '\n'
   '## Чекліст\n'
   '- [x] Тести додано\n'
   '- [x] Документацію оновлено\n',
   ['Опис', 'Як перевірити', 'Чекліст']),
  []),
 ('S2',
  'check_pr_description',
  ('## Опис\n'
   'Додає пошук за назвою\n'
   '\n'
   '## Як перевірити\n'
   'Запустити pytest і відкрити сторінку\n'
   '\n'
   '## Чекліст\n'
   '- [ ] Тести додано\n'
   '- [x] Документацію оновлено\n',
   ['Опис', 'Як перевірити', 'Чекліст']),
  ['Не виконано пункт: Тести додано']),
 ('S2',
  'check_pr_description',
  ('## Опис\n'
   'Додає пошук за назвою\n'
   '\n'
   '## Як перевірити\n'
   'Запустити pytest і відкрити сторінку\n'
   '\n'
   '## Чекліст\n'
   '- [ ] Тести додано\n'
   '- [x] Документацію оновлено\n'
   '- [ ] Оновлено журнал змін\n',
   ['Опис', 'Як перевірити', 'Чекліст']),
  ['Не виконано пункт: Тести додано', 'Не виконано пункт: Оновлено журнал змін']),
 ('S3',
  'check_pr_description',
  ('## Опис\n'
   'Додає пошук за назвою\n'
   '\n'
   '## Як перевірити\n'
   'Запустити pytest і відкрити сторінку\n'
   '\n'
   '## Чекліст\n'
   '- [x] Тести додано\n'
   '- [x] Документацію оновлено\n'
   '\n'
   'Closes #12\n',
   ['Опис', 'Як перевірити', 'Чекліст'],
   'Чекліст',
   True),
  []),
 ('S3',
  'check_pr_description',
  ('## Опис\n'
   'Додає пошук за назвою\n'
   '\n'
   '## Як перевірити\n'
   'Запустити pytest і відкрити сторінку\n'
   '\n'
   '## Чекліст\n'
   '- [x] Тести додано\n'
   '- [x] Документацію оновлено\n',
   ['Опис', 'Як перевірити', 'Чекліст'],
   'Чекліст',
   True),
  ['Немає посилання на задачу']),
 ('S3',
  'check_pr_description',
  ('## Опис\n'
   'Додає пошук за назвою\n'
   '\n'
   '## Як перевірити\n'
   'Запустити pytest і відкрити сторінку\n'
   '\n'
   '## Чекліст\n'
   '- [x] Тести додано\n'
   '- [x] Документацію оновлено\n'
   'Fixes #7',
   ['Опис', 'Як перевірити', 'Чекліст'],
   'Чекліст',
   True),
  [])]


@pytest.mark.parametrize("tag,fn,args,expected", T06, ids=_ids(T06, "T06"))
def test_task_06(tag, fn, args, expected):
    run(6, fn, args, expected)
