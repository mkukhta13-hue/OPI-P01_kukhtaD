"""Відкриті тести задачі 3: Наступна версія за комітами.

Запуск: pytest tests/test_lab_03.py
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


T03 = [('S1', 'next_version', ('1.2.3', ['fix: a']), '1.2.4'),
 ('S1', 'next_version', ('1.2.3', ['feat: a']), '1.3.0'),
 ('S1', 'next_version', ('1.2.3', ['feat!: a']), '2.0.0'),
 ('S2', 'next_version', ('v1.0.0', ['feat: a']), 'v1.1.0'),
 ('S2', 'next_version', ('1.4.2', ['fix: a\n\nBREAKING CHANGE: x']), '2.0.0'),
 ('S2', 'next_version', ('0.3.1', ['feat: a']), '0.3.2'),
 ('S3', 'next_version', ('1.2', []), ValueError('Некоректна версія: 1.2')),
 ('S3', 'next_version', ('x.y.z', ['fix: a']), ValueError('Некоректна версія: x.y.z')),
 ('S3', 'next_version', ('1.2.3-beta', ['fix: a']), ValueError('Некоректна версія: 1.2.3-beta'))]


@pytest.mark.parametrize("tag,fn,args,expected", T03, ids=_ids(T03, "T03"))
def test_task_03(tag, fn, args, expected):
    run(3, fn, args, expected)
