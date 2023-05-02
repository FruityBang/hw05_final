Проект API Yatube - все для общения через API. Связываем людей, связываем жизни.

Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

git clone git@github.com:FruityBang/api_final_yatube.git

cd api_final_yatube

Cоздать и активировать виртуальное окружение:

python3 -m venv env

source env/bin/activate

Установить зависимости из файла requirements.txt:

python3 -m pip install --upgrade pip

pip install -r requirements.txt

Выполнить миграции:

python3 manage.py migrate

Запустить проект:

python3 manage.py runserver

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
