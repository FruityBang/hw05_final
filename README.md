**Проект Yatube - соц.сеть для ведения блогов и общения.**

**Реализована возможность публикации постов с изображениями, подписки на пользователей с
использованием пользовательского интерфейса (HTML, CSS). Регистрация доступна на основе
Generic Views. Написаны тесты (Unittest, TDD).**


Как запустить проект:

- Клонировать репозиторий и перейти в него в командной строке:

  git clone git@github.com:FruityBang/hw05_final.git

  cd hw05_final/

- Cоздать и активировать виртуальное окружение:

  python -m venv venv

  source venv/Scripts/activate (Windows)
  source venv/bin/activate (Linux)

- Установить зависимости из файла requirements.txt:

  python -m pip install --upgrade pip

  pip install -r requirements.txt

- Выполнить миграции:
  cd yatube/

  python manage.py migrate

- Запустить проект:

  python manage.py runserver

Примеры.

Доступные эндпоинты:

http://127.0.0.1:8000/api/v1/posts/

http://127.0.0.1:8000/api/v1/groups/

http://127.0.0.1:8000/api/v1/follow/

http://127.0.0.1:8000/api/v1/jwt/

Запросы:

POST http://127.0.0.1:8000/api/v1/posts/ { "text": "string", "image": "string", "group": 0 }

POST http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/ { "text": "string" }

POST http://127.0.0.1:8000/api/v1/follow/ { "following": "string" }
