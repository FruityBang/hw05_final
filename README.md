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

***Доступные эндпоинты:***

http://127.0.0.1:8000/

http://127.0.0.1:8000/admin/

http://127.0.0.1:8000/about/

http://127.0.0.1:8000/auth/

http://127.0.0.1:8000/group/slug/

http://127.0.0.1:8000/posts/post_id/
