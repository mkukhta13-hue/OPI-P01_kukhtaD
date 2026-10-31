def merge_lines(base: list[str], ours: list[str], theirs: list[str], style: str = "merge") -> dict:
    # 1. Перевірка стилю (виконується першою за правилами)
    if style not in ("merge", "diff3"):
        raise ValueError(f"Невідомий стиль: {style}")

    # 2. Перевірка довжини списків
    if len(base) != len(ours) or len(base) != len(theirs):
        raise ValueError("Версії мають різну кількість рядків")

    merged_lines = []
    conflicts_count = 0
    
    in_conflict = False
    conflict_ours = []
    conflict_base = []
    conflict_theirs = []

    def flush_conflict():
        nonlocal in_conflict, conflict_ours, conflict_base, conflict_theirs, conflicts_count
        if not in_conflict:
            return
        
        conflicts_count += 1
        merged_lines.append("<<<<<<< ours")
        merged_lines.extend(conflict_ours)
        if style == "diff3":
            merged_lines.append("||||||| base")
            merged_lines.extend(conflict_base)
        merged_lines.append("=======")
        merged_lines.extend(conflict_theirs)
        merged_lines.append(">>>>>>> theirs")

        # Очищення тимчасових списків конфлікту
        in_conflict = False
        conflict_ours = []
        conflict_base = []
        conflict_theirs = []

    for b, o, t in zip(base, ours, theirs):
        if o == t:
            # Зміни однакові з обох сторін
            flush_conflict()
            merged_lines.append(o)
        elif o == b:
            # Змінено тільки в theirs
            flush_conflict()
            merged_lines.append(t)
        elif t == b:
            # Змінено тільки в ours
            flush_conflict()
            merged_lines.append(o)
        else:
            # Конфліктна позиція (обидва змінили по-різному)
            in_conflict = True
            conflict_ours.append(o)
            conflict_base.append(b)
            conflict_theirs.append(t)

    # Якщо файл закінчився в стані конфлікту
    flush_conflict()

    return {
        "lines": merged_lines,
        "conflicts": conflicts_count
    }