import requests
import uuid

from src.db.models import products
from src.db.models import history_requests
from sqlalchemy import insert, select, update
from src.db.database import get_async_session
from src.db.schemas import GetProductsFromDB


async def get_data_product(vendor_code: str, user_id: int) -> str:
    """
    Асинхронная функция для получения данных о продукте и их сохранения для указанного пользователя.

    Args:
    - vendor_code (str): Артикул продукта.
    - user_id (int): Идентификатор пользователя.

    Returns:
    - str или другой тип данных: Ответ боту или сообщение об ошибке.
    """
    response = requests.get(
        f'https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={vendor_code}')
    if response.status_code == 200:
        data = response.json()["data"]["products"][0]
        qty = sum(stock['qty'] for size in data['sizes'] for stock in size['stocks'])
        all_data_product = [data['name'], data['id'], data["priceU"], data['reviewRating'], qty]
        answer = await answer_for_bot(all_data_product)
        await save_new_product(all_data_product, user_id)
        return answer
    else:
        return 'Ошибка при отправке запроса.'


async def answer_for_bot(product: list) -> str:
    """
   Асинхронная функция, которая форматирует данные о продукте для ответа боту.

   Args:
   - product (list): Список данных о продукте в следующем порядке:
                     [название продукта, артикул, цена, рейтинг отзывов, количество на складе].

   Returns:
   - str: Отформатированный ответ для бота.
   """
    formatted_price = await format_price(product[2])
    answer = f"Название товара: {product[0]}\n" \
             f"Артикул: {product[1]}\n" \
             f"Цена: {formatted_price} руб.\n" \
             f"Рейтинг: {product[3]}\n" \
             f"Кол-во на складах: {product[4]}"
    return answer


async def save_new_product(new_values: list, user_id: int) -> None:
    """
    Асинхронная функция для сохранения новых данных о продукте для указанного пользователя.

    Args:
    - new_values (list): Список новых значений данных о продукте в следующем порядке:
                         [название продукта, артикул, цена, рейтинг отзывов, количество на складе, идентификатор].
    - user_id (int): Идентификатор пользователя.

    Returns:
    - None
    """
    async for session in get_async_session():
        stmt = select(products.c.id).where(products.c.vendor_code == str(new_values[1]))
        result = await session.execute(stmt)
        if not result.scalar():
            id_uuid = uuid.uuid4()
            new_values.append(id_uuid)
            stmt = insert(products).values(id=new_values[5], name=new_values[0],
                                           vendor_code=str(new_values[1]), price=new_values[2],
                                           rating=new_values[3], qty=new_values[4], user_id=str(user_id))
        else:
            stmt = update(products).where(products.c.vendor_code == str(new_values[1])).values(
                name=new_values[0], price=new_values[2], rating=new_values[3], qty=new_values[4])

        await session.execute(stmt)
        await session.commit()


async def get_last_product(user_id: int) -> list[GetProductsFromDB]:
    """
   Асинхронная функция для получения последних записей продуктов пользователя из базы данных.

   Args:
   - user_id: Идентификатор пользователя.

   Returns:
   - list[GetProductsFromDB]: Список объектов с данными о продуктах из базы данных
   - str в случае, если в базе данных нет записей пользователя.
   """
    async for session in get_async_session():
        all_answer = ''
        fields = [products.c.name, products.c.vendor_code, products.c.price, products.c.rating, products.c.qty]
        stmt = select(*fields).where(products.c.user_id == str(user_id)).order_by(products.c.id.desc()).limit(5)
        answer_db = await session.execute(stmt)
        rezult_data = [[data.name, data.vendor_code,
                        data.price, data.rating, data.qty] for data in answer_db]
        if rezult_data:
            for i in rezult_data:
                answer = await answer_for_bot(i)
                all_answer += answer
                all_answer += "\n\n"
            return all_answer
        else:
            return "В базе данных нет ваших записей"


async def save_request(new_values: dict):
    """
    Асинхронная функция для сохранения нового запроса в истории запросов.

    Args:
    - new_values (Request): Объект Request, содержащий новые значения для запроса.

    Returns:
    - None
     """
    async for session in get_async_session():
        stmt = insert(history_requests).values(id=new_values["id"], user_id=new_values["user_id"],
                                               vendor_code=new_values["vendor_code"],
                                               date_request=new_values["date_request"])
        await session.execute(stmt)
        await session.commit()


async def format_price(price):
    """
    Асинхронная функция для форматирования цены.

    Args:
    - price: Цена продукта.

    Returns:
    - str: Отформатированная цена.

    """
    rubles, kopecks = divmod(price, 100)
    formatted_price = "{:.2f}".format(rubles + kopecks / 1000)
    return formatted_price
