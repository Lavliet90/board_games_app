from datetime import datetime


def validate_date(date_text):
    try:
        input_date = datetime.strptime(date_text, "%Y-%m-%d %H:%M")
        if input_date >= datetime.now():
            return True, None
        else:
            return (
                False,
                "Дата в прошлом. Пожалуйста, введите дату и время позже, чем сейчас",
            )
    except ValueError:
        return (
            False,
            "Неверный формат даты. Пожалуйста, введите дату в формате YYYY-MM-DD HH:MM:",
        )
