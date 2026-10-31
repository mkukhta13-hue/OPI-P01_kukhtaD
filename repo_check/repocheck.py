"""Перевірник частини Б: локальний репозиторій команди.

Використання: python repo_check/repocheck.py [шлях_до_репозиторію]   (за замовчуванням team-repo)
Або через pytest: REPO=team-repo pytest repo_check
Перевірник працює офлайн: лише git і файли. Кожне зауваження виводиться окремим рядком.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CONVENTIONAL = re.compile(r"(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(\([^()\s]+\))?!?: .+")
BRANCH_TRUNK = re.compile(r"(feature|fix|docs|chore)/[1-9][0-9]*-[a-z0-9]+(-[a-z0-9]+)*")
BRANCH_FLOW = re.compile(r"(feature|bugfix)/[1-9][0-9]*-[a-z0-9]+(-[a-z0-9]+)*|(release|hotfix)/[0-9]+\.[0-9]+\.[0-9]+")
MERGE_SUBJECT = re.compile(r"Merge branch '([^']+)'")
PR_SECTIONS = ["Опис", "Як перевірити", "Чекліст"]
COLUMNS = {"Backlog", "Todo", "In progress", "In review", "Done"}
COMMENT = re.compile(r"- \S+:[0-9]+ [—–-] \[(blocking|suggestion|nit)\] .{5,}")
ENV = dict(os.environ, GIT_AUTHOR_NAME="Перевірник", GIT_AUTHOR_EMAIL="check@example.test",
           GIT_COMMITTER_NAME="Перевірник", GIT_COMMITTER_EMAIL="check@example.test",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull, LC_ALL="C.UTF-8")


def git(repo, *args, check=False):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=ENV, encoding="utf-8")
    if check and proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc


def show(repo, rev, path):
    proc = git(repo, "show", f"{rev}:{path}")
    return proc.stdout if proc.returncode == 0 else None


def sections(md):
    """Повертає {назва_розділу: текст} для заголовків другого рівня."""
    result, name = {}, None
    for line in md.split("\n"):
        if line.startswith("## "):
            name = line[3:].strip()
            result[name] = ""
        elif name is not None:
            result[name] += line + "\n"
    return result


def check_repo(path) -> list[str]:
    repo = Path(path).resolve()
    errors = []
    if shutil.which("git") is None:
        return ["git не знайдено: встановіть git"]
    if not (repo / ".git").exists():
        return [f"{repo} не є репозиторієм git (виконайте git init)"]
    branches = git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.split()
    if "main" not in branches:
        return ["немає гілки main (git branch -M main)"]
    flow_md = show(repo, "main", "docs/BRANCHING.md") or ""
    m = re.search(r"^Стратегія: (Git Flow|trunk-based)\s*$", flow_md, re.M)
    if not m:
        errors.append("docs/BRANCHING.md у main: немає рядка «Стратегія: Git Flow» або «Стратегія: trunk-based»")
        gitflow = False
    else:
        gitflow = m.group(1) == "Git Flow"
    if gitflow and "develop" not in branches:
        errors.append("стратегія Git Flow, але немає гілки develop")
    # --- захист main (хук у репозиторії)
    hook = show(repo, "main", "hooks/pre-commit")
    if hook is None:
        errors.append("у main немає файлу hooks/pre-commit")
    else:
        tmp = Path(tempfile.mkdtemp())
        try:
            clone = tmp / "c"
            git(tmp, "clone", "-q", str(repo), str(clone))
            git(clone, "checkout", "-q", "main")
            hp = ["-c", "core.hooksPath=hooks"]
            os.chmod(clone / "hooks" / "pre-commit", 0o755)
            bad = git(clone, *hp, "commit", "--allow-empty", "-m", "chore: прямий коміт")
            if bad.returncode == 0:
                errors.append("хук hooks/pre-commit не забороняє прямий коміт у main")
            git(clone, "checkout", "-q", "-b", "feature/1-probe")
            good = git(clone, *hp, "commit", "--allow-empty", "-m", "chore: пробний коміт")
            if good.returncode != 0:
                errors.append("хук hooks/pre-commit блокує коміти у робочих гілках: " + good.stderr.strip()[:80])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    cfg = git(repo, "config", "--get", "core.hooksPath").stdout.strip()
    if cfg != "hooks":
        errors.append("не виконано git config core.hooksPath hooks (хуки з репозиторію не підключено)")
    # --- історія
    target = "develop" if gitflow else "main"
    if target not in branches:
        target = "main"
    log = git(repo, "log", "main", *(["develop"] if "develop" in branches else []), "--format=%H|%P|%s").stdout.splitlines()
    commits = [l.split("|", 2) for l in log]
    plain = [c for c in commits if len(c[1].split()) < 2]
    merges = [c for c in commits if len(c[1].split()) >= 2]
    if len(plain) < 8:
        errors.append(f"у історії {len(plain)} звичайних комітів (потрібно щонайменше 8)")
    bad = [c[2] for c in plain if not CONVENTIONAL.fullmatch(c[2])]
    if bad:
        errors.append(f"коміти не за Conventional Commits ({len(bad)}), наприклад: «{bad[0]}»")
    names = []
    rx = BRANCH_FLOW if gitflow else BRANCH_TRUNK
    for _, _, subject in merges:
        mm = MERGE_SUBJECT.match(subject)
        if mm and mm.group(1) not in ("main", "develop"):
            names.append(mm.group(1))
    names = sorted(set(names))
    if len(names) < 3:
        errors.append(f"злито {len(names)} робочих гілок через merge-коміт (потрібно щонайменше 3, git merge --no-ff)")
    for name in names:
        if not rx.fullmatch(name):
            errors.append(f"назва гілки «{name}» не відповідає стратегії")
    # --- конфлікт
    resolved = False
    for sha, parents, _ in merges:
        p = parents.split()
        if len(p) != 2:
            continue
        base = git(repo, "merge-base", p[0], p[1]).stdout.strip()
        if not base:
            continue
        left = set(git(repo, "diff", "--name-only", base, p[0]).stdout.split())
        right = set(git(repo, "diff", "--name-only", base, p[1]).stdout.split())
        text = git(repo, "log", "-1", "--format=%B", sha).stdout.lower()
        if left & right and "конфлікт" in text:
            resolved = True
    if not resolved:
        errors.append("немає злиття з вирішеним конфліктом (обидві гілки змінили один файл, у повідомленні злиття слово «конфлікт»)")
    leftovers = git(repo, "grep", "-n", "-E", "^(<<<<<<<|>>>>>>>)( |$)", "main", "--", ".").stdout.strip()
    if leftovers:
        errors.append("у main залишились маркери конфлікту: " + leftovers.splitlines()[0][:80])
    # --- шаблон PR, DoD
    tpl = show(repo, "main", ".github/pull_request_template.md")
    if tpl is None:
        errors.append("немає .github/pull_request_template.md у main")
    else:
        have = sections(tpl)
        for s in PR_SECTIONS:
            if s not in have:
                errors.append(f"шаблон PR: немає розділу «## {s}»")
    contrib = show(repo, "main", "CONTRIBUTING.md")
    if contrib is None:
        errors.append("немає CONTRIBUTING.md у main")
    else:
        dod = sections(contrib).get("Definition of Done")
        if dod is None:
            errors.append("CONTRIBUTING.md: немає розділу «## Definition of Done»")
        elif len([l for l in dod.split("\n") if re.match(r"\s*[-*] \S", l)]) < 4:
            errors.append("Definition of Done: потрібно щонайменше 4 пункти списку")
    # --- pull request і рецензії як файли
    ls = git(repo, "ls-tree", "-r", "--name-only", "main").stdout.split("\n")
    prs = sorted(p for p in ls if re.fullmatch(r"pull_requests/PR-[0-9]+\.md", p))
    if len(prs) < 3:
        errors.append(f"pull_requests/PR-NNN.md: {len(prs)} файлів (потрібно щонайменше 3)")
    for p in prs:
        have = sections(show(repo, "main", p) or "")
        for s in PR_SECTIONS:
            body = have.get(s)
            if body is None:
                errors.append(f"{p}: немає розділу «## {s}»")
            elif len(re.findall(r"\w+", body)) < 3:
                errors.append(f"{p}: розділ «{s}» порожній")
        if re.search(r"- \[ \]", show(repo, "main", p) or ""):
            errors.append(f"{p}: у чекліст лишились невиконані пункти")
    revs = sorted(p for p in ls if re.fullmatch(r"reviews/REVIEW-[0-9]+\.md", p))
    if len(revs) < 2:
        errors.append(f"reviews/REVIEW-NNN.md: {len(revs)} файлів (потрібно щонайменше 2)")
    decisions = []
    for p in revs:
        text = show(repo, "main", p) or ""
        count = len([l for l in text.split("\n") if COMMENT.fullmatch(l.strip())])
        if count < 3:
            errors.append(f"{p}: {count} коментарів формату «- файл:рядок — [blocking|suggestion|nit] текст» (потрібно щонайменше 3)")
        d = re.search(r"^Рішення: (Схвалено|Запитано зміни)\s*$", text, re.M)
        if not d:
            errors.append(f"{p}: немає рядка «Рішення: Схвалено» або «Рішення: Запитано зміни»")
        else:
            decisions.append(d.group(1))
    if revs and "Запитано зміни" not in decisions:
        errors.append("жодна рецензія не містить рішення «Запитано зміни»")
    # --- дошка
    board = show(repo, "main", "BOARD.md")
    if board is None:
        errors.append("немає BOARD.md у main")
    else:
        rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in board.split("\n")
                if l.strip().startswith("|") and not re.fullmatch(r"[|\s:-]+", l.strip())]
        rows = [r for r in rows if len(r) >= 4 and r[0] != "Задача"]
        if len(rows) < 6:
            errors.append(f"BOARD.md: {len(rows)} карток у таблиці (потрібно щонайменше 6)")
        badcol = sorted({r[1] for r in rows if r[1] not in COLUMNS})
        if badcol:
            errors.append(f"BOARD.md: невідомі колонки {badcol}")
        if sum(1 for r in rows if r[1] == "Done") < 2:
            errors.append("BOARD.md: щонайменше 2 картки мають бути в колонці Done")
        wip = re.search(r"WIP-ліміт[^0-9\n]*([0-9]+)", board)
        if not wip:
            errors.append("BOARD.md: немає рядка «WIP-ліміт In progress: N»")
        elif sum(1 for r in rows if r[1] == "In progress") > int(wip.group(1)):
            errors.append("BOARD.md: карток In progress більше за WIP-ліміт")
        if not re.search(r"^Мета спринту: \S", board, re.M):
            errors.append("BOARD.md: немає рядка «Мета спринту: ...»")
    return errors


def main(argv):
    path = argv[1] if len(argv) > 1 else "team-repo"
    errors = check_repo(path)
    for e in errors:
        print("-", e)
    print("Зауважень:", len(errors))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
