from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    now = datetime.today().strftime('%Y')
    return {
        'year': now,
    }
