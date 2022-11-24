from aiohttp import web
import asyncpg

#параменты подключения к БД Postgres
DB_NAME = "innopolis"
DB_HOST = "127.0.0.1"
DB_PORT = "55005"
DB_USER = "postgres"
DB_PASSWORD = "postgrespw"
POOL_MIN_SIZE = 5
POOL_MAX_SIZE = 10

#SQL запросы для эндпойнтов
SQL_GET_ITEMS = '''select * from item;'''
SQL_GET_STORES = '''select * from store;'''
SQL_GET_MONTH_TOP_STORES = '''select st.id, st.address, sum(i.price) as revenue
                            from sales s
                            join store st on st.id = s.store_id
                            join item i on i.id = s.item_id
                            where s.sale_time >= now() - interval '1 month'
                            group by st.id, st.address
                            order by revenue desc
                            limit 10;'''
SQL_GET_TOP_ITEMS = '''select i.id, i.item_name, count(*) as cnt
                    from sales s
                    join item i on s.item_id = i.id
                    group by i.id, i.item_name
                    order by cnt desc
                    limit 10;'''
SQL_SALE = '''insert into sales(item_id, store_id) VALUES($1, $2);'''


routes = web.RouteTableDef()

async def fetch_rows(sql_query: str):
    '''
    Выполняет запрос в БД по выборке строк из таблицы
    параметры:
        sql_query (str) : SQL запрос для выборки данных
    результат:
        Возвращает список словарей соответствующие строкам выбранных данных
    '''
    conn = app['DB_POOL']
    values = await conn.fetch(sql_query)

    res = []
    for row in values:
        res.append({key:val for key, val in row.items()})

    return res

@routes.get('/get_items')
async def get_items(request):
    '''
    Обрабатывает GET-запрос на получение всех товарных позиций
    '''
    return web.json_response(await fetch_rows(sql_query=SQL_GET_ITEMS))

@routes.get('/get_stores')
async def get_stores(request):
    '''
    Обрабатывает GET-запрос на получение всех магазинов
    '''
    return web.json_response(await fetch_rows(sql_query=SQL_GET_STORES))

@routes.get('/get_month_top_stores')
async def get_month_top_stores(request):
    '''
    Обрабатывает GET-запрос на получение данных по топ 10 самых доходных магазинов за месяц (id + адреса + суммарная выручка)
    '''
    return web.json_response(await fetch_rows(sql_query=SQL_GET_MONTH_TOP_STORES))

@routes.get('/get_top_items')
async def get_top_items(request):
    '''
    Обрабатывает GET-запрос на получение данных по топ 10 самых продаваемых товаров (id + наименование + количество проданных товаров)
    '''
    return web.json_response(await fetch_rows(sql_query=SQL_GET_TOP_ITEMS))


@routes.post('/sale')
async def sale(request):
    '''
    Обрабатывает POST-запрос с json-телом для сохранения данных о произведенной продаже (id товара + id магазина)
    '''
    body = await request.json()
    if 'item_id' in body and 'store_id' in body:
        conn = app['DB_POOL']
        await conn.execute(SQL_SALE, int(body['item_id']), int(body['store_id']))
        return web.Response(status=201)
    else:
        return web.Response(text='Bad request')


async def connection_open(app):
    '''
    Создает пул подключений к БД Postgres
    параметры:
        web.Application
    '''
    pool = await asyncpg.create_pool(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME,min_size=POOL_MIN_SIZE, max_size=POOL_MAX_SIZE)

    app['DB_POOL'] = pool

async def connection_close(app):
    '''
    Закрывает пул подключений к БД Postgres
    параметры:
        web.Application
    '''
    await app['DB_POOL'].close()

if __name__ == "__main__":
    app = web.Application()
    app.on_startup.append(connection_open)
    app.on_cleanup.append(connection_close)
    app.add_routes(routes)
    web.run_app(app)
