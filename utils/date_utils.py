# выделение функц работы с датами
# для переиспользования и тестов

from datetime import datetime

def auto_format_date_live(raw: str) -> str:

    #реобразует вводимые цифры в формат ДД.ММ.ГГГГ ЧЧ:ММ
    digits = "".join(c for c in raw if c.isdigit())
    formatted = ""

    if len(digits) > 0:
        formatted += digits[:2]
    if len(digits) > 2:
        formatted += "." + digits[2:4]
    if len(digits) > 4:
        formatted += "." + digits[4:8]
    if len(digits) > 8:
        formatted += " " + digits[8:10]
    if len(digits) > 10:
        formatted += ":" + digits[10:12]

    return formatted


def get_time_left(deadline: str) -> str:
    #возвращает строку с оставшимся временем до дедлайна
    if not deadline:
        return "без срока"
    try:
        d = datetime.strptime(deadline, "%d.%m.%Y %H:%M")
        diff = d - datetime.now()
        if diff.total_seconds() < 0:
            return "⛔ просрочено"
        return f"{diff.days}д {diff.seconds // 3600}ч"
    except:
        return "?"


def validate_deadline(deadline: str) -> bool:
    #проверяет на соответствие строку, формату дедлайна
    if not deadline:
        return True
    try:
        datetime.strptime(deadline, "%d.%m.%Y %H:%M")
        return True
    except:
        return False