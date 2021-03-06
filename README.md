# Yandex Backend Test
REST API с использованием Flask, SQLAlchemy и Marshmallow

## Зависимости

Для работы приложения необходима версия языка ```Python 3.6``` и выше

Зависимости для проекта описаны в файлах ```Pipfile``` и ```Pipfile.lock```
или в файле ```requirements.txt```:

```
Click==7.0
Flask==1.1.1
flask-marshmallow==0.10.1
Flask-SQLAlchemy==2.4.0
gunicorn==19.9.0
itsdangerous==1.1.0
Jinja2==2.10.1
MarkupSafe==1.1.1
marshmallow==3.0.1
marshmallow-sqlalchemy==0.17.0
numpy==1.17.0
psycopg2==2.8.3
redis==3.3.8
simplejson==3.16.0
six==1.12.0
SQLAlchemy==1.3.7
Werkzeug==0.15.5
```

## Утановка
Установка и развертывание

```
sudo apt-get install python3 python3-pip postgresql postgresql-contrib libpq-dev redis-server
cd /var && git clone https://github.com/kholmatov/Yandex-Backend-Test.git
cd Yandex-Backend-Test
```
Установка зависимых пакетов:  
```
pip install flask flask_sqlalchemy psycopg2-binary gunicorn marshmallow marshmallow-sqlalchemy numpy
```

или

```pip install -r requirements.txt``` 

Далее необходимо создать БД ```api``` и нового пользователя ```yandex``` с паролем ```apidbpassword``` 
```
sudo -u postgres psql
create database api;
create user yandex with encrypted password 'apidbpassword';
grant all privileges on database api to yandex;
\q
```
После запускаем python и создаем своих таблиц в базе данных PostgreSQL
```
$ python
>> from app import db
>> db.create_all()
>> exit()
```

## Запуск сервера

В папке приложения

```gunicorn -b 0.0.0.0:8080 app:app```

В папке ```/etc/systemd/system``` надо создать ```gunicorn.service``` со следующим содержанием
```
[Service]
User=entrant
WorkingDirectory=/var/Yandex-Backend-Test
ExecStart=/usr/bin/gunicorn --bind 0.0.0.0:8080 app:app
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```
Дальше открываем консоль и заставляем всё это работать
```
sudo systemctl enable gunicorn.service
sudo systemctl start gunicorn.service
```
 
## Методы API

```POST /imports``` Принимает на вход набор с данными о жителях в формате json и сохраняет его с уникальным идентификатором.

```PATCH /imports/<int:import_id>/citizens/<int:citizen_id>``` Изменяет информацию о жителе в указанном наборе данных. На вход подается JSON в котором можно указать любые данные о жителе (name, gender, birth_date, relatives, town, street, building, appartement), кроме citizen_id.

```GET /imports/<int:import_id>/citizens``` Возвращает список всех жителей для указанного набора данных

```GET /imports/<int:import_id>/citizens/birthdays``` Возвращает жителей и количество подарков, которые они будут покупать своим ближайшим родственникам (1-го порядка), сгруппированных по месяцам из указанного набора данных

```GET /imports/<int:import_id>/towns/stat/percentile/age``` Возвращает статистику по городам для указанного набора данных в разрезе возраста жителей: p50, p75, p99, где число - это значение перцентиля

## Тесты

```tests/tests.py``` - тесты на нагрузку и проверка API запросов
