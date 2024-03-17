from datetime import datetime

from sqlalchemy import Table, Column, Uuid, String, Integer, Float, TIMESTAMP

from src.db.database import metadata

products = Table(
	'''
	Описание:
	Таблица "products" представляет собой таблицу в базе данных, которая хранит информацию о продуктах.
	
	Структура:
	- Колонка "id" - уникальный идентификатор продукта типа Uuid.
	- Колонка "name" - название продукта (строка длиной до 100 символов), не может быть пустой.
	- Колонка "vendor_code" - артикул продукта (строка длиной до 50 символов), не может быть пустой.
	- Колонка "price" - цена продукта (целое число), значение по умолчанию - 0.
	- Колонка "rating" - рейтинг продукта (число с плавающей точкой), значение по умолчанию - 0.0.
	- Колонка "qty" - количество продукта на складе (целое число), значение по умолчанию - 0.
	- Колонка "user_id" - идентификатор пользователя (строка), не может быть пустой.
	'''
	'products',
	metadata,
	Column('id', Uuid, primary_key=True),
	Column('name', String(100), nullable=False),
	Column('vendor_code', String(50), nullable=False),
	Column('price', Integer, default=0),
	Column('rating', Float, default=0.0),
	Column('qty', Integer, default=0),
	Column('user_id', String, nullable=False),
)

history_requests = Table(
	'''
	Описание:
	Таблица "history_requests" представляет собой таблицу в базе данных, которая хранит информацию о запросах пользователей.
	
	Структура:
	- Колонка "id" - уникальный идентификатор запроса типа Uuid.
	- Колонка "user_id" - идентификатор пользователя (строка), не может быть пустой.
	- Колонка "date_request" - дата и время запроса (тип TIMESTAMP), значение по умолчанию - текущая дата и время, не может быть пустой.
	- Колонка "vendor_code" - артикул продукта (строка длиной до 50 символов), не может быть пустой.
	'''
	'history_requests',
	metadata,
	Column('id', Uuid, primary_key=True),
	Column('user_id', String, nullable=False),
	Column("date_request", TIMESTAMP, default=datetime.utcnow(), nullable=False),
	Column('vendor_code', String(50), nullable=False)
)
