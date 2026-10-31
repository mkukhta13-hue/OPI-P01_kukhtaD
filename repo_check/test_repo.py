"""Перевірка частини Б: pytest repo_check (шлях до репозиторію — змінна REPO, за замовчуванням team-repo)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repocheck import check_repo  # noqa: E402


def test_repo_has_no_issues():
    errors = check_repo(os.environ.get("REPO", "team-repo"))
    assert not errors, "\n" + "\n".join("- " + e for e in errors)
