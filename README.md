Готовый проект:
http://158.160.43.59/

Запуск проекта в контейнерах
Клонирование удаленного репозитория
git clone git@github.com:AliceYaroslavtseva/foodgram-project-react.git
cd infra
В директории /infra создайте файл .env, с переменными окружения, используя образец .env.example
Сборка и развертывание контейнеров
docker-compose up -d --build
Выполните миграции, соберите статику, создайте суперпользователя
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py createsuperuser
Наполните базу данных ингредиентами и тегами
docker-compose exec backend python manage.py load_data
или наполните базу тестовыми данными (включают посты и пользователей)
docker-compose exec backend python manage.py loaddata data/data.json 
Стандартная админ-панель Django доступна по адресу https://localhost/admin/
Документация к проекту доступна по адресу https://localhost/api/docs/
Запуск API проекта в dev-режиме
Клонирование удаленного репозитория (см. выше)
Создание виртуального окружения и установка зависимостей
cd backend
python -m venv venv
. venv/Scripts/activate (windows)
. venv/bin/activate (linux)
pip install --upgade pip
pip install -r -requirements.txt
Примените миграции и соберите статику
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
Наполнение базы данных ингредиентами и тегами
python manage.py load_data
в файле foodgram/setting.py замените БД на встроенную SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
Запуск сервера
python manage.py runserver 