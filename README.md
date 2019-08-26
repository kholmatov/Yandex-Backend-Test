# Yandex Backend Test
REST API с использованием Flask, SQLAlchemy и Marshmallow

## Список зависимости
```bash
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
six==1.12.0
SQLAlchemy==1.3.7
Werkzeug==0.15.5
```
## Утановка
Установка и развертывание

```
sudo apt-get install python3-pip postgresql postgresql-contrib libpq-dev redis-server
pip3 install flask flask_sqlalchemy psycopg2-binary gunicorn marshmallow marshmallow-sqlalchemy numpy
git clone https://github.com/kholmatov/Yandex-Backend-Test.git
```
Далее необходимо установить пароль для postgres и создать БД для тестов
```
sudo -u postgres psql
alter user postgres with encrypted password 'postgres';
create database api;
\q
```

## Запуск сервера

В папке приложения

```gunicorn -b 0.0.0.0:8080 app:app```

В папке ```/etc/systemd/system``` надо создать ```gunicorn.service``` со следующим содержанием
```
[Service]
User=entrant
WorkingDirectory=/var/yandex/flask
ExecStart=/home/entrant/.local/share/virtualenvs/flask-vGj3Vvuz/bin/gunicorn --bind 0.0.0.0:8080 app:app
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

```tests/tests.py``` - тесты на нагрузку<br/>
```tests/data``` - папка с демо данными для генерации citizens 
