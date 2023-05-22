## *Готовый проект: http://158.160.43.59/*
---

## 1. [Описание](#1)
## 2. [Установка Docker](#2)
## 3. [База данных и переменные окружения](#3)
## 4. [Команды для запуска](#4)
## 5. [Заполнение базы данных](#5)
## 6. [Техническая информация](#6)
## 7. [Об авторе](#7)

---
## 1. Описание <a id=1></a>

Проект "Продуктовый помощник" (Foodgram) предоставляет пользователям следующие возможности:
  - регистрация;
  - создание своих рецептов и управление ими: изменение и удаление;
  - просмотр рецептов других пользователей;
  - добавление рецептов в "Избранное" и "Корзину";
  - подписка на других пользователей;
  - скачивание списока ингредиентов, добавленных в "Корзину".

---
## 2. Установка Docker <a id=2></a>

- Установить на сервере Docker, Docker Compose:

```
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin              # последняя версия docker compose
```

- Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):

```
scp docker-compose.yml nginx.conf username@IP:/home/username/   # username - имя пользователя на сервере
                                                                # IP - публичный IP сервера
```

---
## 3. База данных и переменные окружения <a id=3></a>

Проект использует базу данных PostgreSQL.  
Для подключения и выполненя запросов к базе данных необходимо создать и заполнить файл ".env" с переменными окружения в папке "./infra/".
Шаблон для заполнения файла ".env":

```
DB_ENGINE               # django.db.backends.postgresql
DB_NAME                 # postgres
POSTGRES_USER           # postgres
POSTGRES_PASSWORD       # postgres
DB_HOST                 # db
DB_PORT                 # 5432 (порт по умолчанию)
```

Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:

```
SECRET_KEY              # секретный ключ Django проекта
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # *если ssh-ключ защищен паролем
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение
```
Локально лучше использовать sqlite3, настройки:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

---
## 4. Команды для запуска <a id=4></a>

Перед запуском необходимо склонировать проект:
```bash
HTTPS: git clone https://github.com/AliceYaroslavtseva/foodgram-project-react.git
SSH: git clone git@github.com:AliceYaroslavtseva/foodgram-project-react.git
```

Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```

И установить зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Далее необходимо собрать образы для фронтенда и бэкенда.  
Из папки "./backend/" выполнить команду:
```bash
docker build -t alice08/foodgram_backend .
```

Из папки "./frontend/" выполнить команду:
```bash
docker build -t alice08/foodgram_frontend .
```

После создания образов можно создавать и запускать контейнеры.  
Из папки "./infra/" выполнить команду:
```bash
docker-compose up -d
```

После успешного запуска контейнеров выполнить миграции:
```bash
docker-compose exec backend python manage.py migrate
```

Создать суперюзера (Администратора):
```bash
docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

Теперь доступность проекта можно проверить по адресу [http://localhost/](http://localhost/)

---
## 5. Заполнение базы данных <a id=5></a>

С проектом поставляются данные об ингредиентах и тегах.  
Заполнить базу данных ингредиентами можно выполнив следующую команду из папки "./infra/":
```bash
docker-compose exec backend python manage.py load_ingredients
```

---
## 6. Техническая информация <a id=6></a>

Стек технологий: Python 3, Django, Django Rest, React, Docker, PostgreSQL, nginx, gunicorn, Djoser.

Веб-сервер: nginx (контейнер nginx)  
Frontend фреймворк: React (контейнер frontend)  
Backend фреймворк: Django (контейнер backend)  
API фреймворк: Django REST (контейнер backend)  
База данных: PostgreSQL (контейнер db)

Веб-сервер nginx перенаправляет запросы клиентов к контейнерам frontend и backend, либо к хранилищам (volume) статики и файлов.  
Контейнер nginx взаимодействует с контейнером backend через gunicorn.  
Контейнер frontend взаимодействует с контейнером backend посредством API-запросов.

---
## 7. Об авторе <a id=7></a>

Ярославцева Алиса Владимировна
Python-разработчик (Backend)  
Россия, г. Тольятти 
E-mail: yaroslavtsevaalisa@yandex.ru  
Telegram: @hellfoxalice
