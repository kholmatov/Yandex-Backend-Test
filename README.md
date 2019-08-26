# Yandex Backend Test
REST API с использованием Flask, SQLAlchemy и Marshmallow

## Утановка

## Технологии
```bash
Click==7.0
Flask==1.1.1
flask-marshmallow==0.10.1
Flask-SQLAlchemy==2.4.0
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
 
## Методы API

```POST /imports``` Принимает на вход набор с данными о жителях в формате json и сохраняет его с уникальным идентификатором.

```PATCH /imports/<int:import_id>/citizens/<int:citizen_id>``` Изменяет информацию о жителе в указанном наборе данных. На вход подается JSON в котором можно указать любые данные о жителе (name, gender, birth_date, relatives, town, street, building, appartement), кроме citizen_id.

```GET /imports/<int:import_id>/citizens``` Возвращает список всех жителей для указанного набора данных

```GET /imports/<int:import_id>/citizens/birthdays``` Возвращает жителей и количество подарков, которые они будут покупать своим ближайшим родственникам (1-го порядка), сгруппированных по месяцам из указанного набора данных

```GET /imports/<int:import_id>/towns/stat/percentile/age``` Возвращает статистику по городам для указанного набора данных в разрезе возраста жителей: p50, p75, p99, где число - это значение перцентиля
