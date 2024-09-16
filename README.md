# innopolis_tasks
Задания Иннополис

h1. ДЗ1 Асинхронность


dz_async.py - Реализует асинхронное веб приложение

В качестве БД используется Postgres
В качестве асинхронного веб-фреймворка используется aiohttp
В качестве асинхронного драйвера подключения к БД используется asyncpg

h2. Эндпойнты:
http://127.0.0.1:8080/get_items - обрабатывает GET-запрос на получение всех товарных позиций
http://127.0.0.1:8080/get_stores - обрабатывает GET-запрос на получение всех магазинов
http://127.0.0.1:8080/sale - обрабатывает POST-запрос с json-телом для сохранения данных о произведенной продаже (id товара + id магазина)
http://127.0.0.1:8080/get_month_top_stores - обрабатывает GET-запрос на получение данных по топ 10 самых доходных магазинов за месяц (id + адреса + суммарная выручка)
http://127.0.0.1:8080/get_top_items - обрабатывает GET-запрос на получение данных по топ 10 самых продаваемых товаров (id + наименование + количество проданных товаров)

Параметры подключения к БД задаются в файле dz_async.py через переменные DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, POOL_MIN_SIZE, POOL_MAX_SIZE

h2. Модель данных:

CREATE TABLE IF NOT EXISTS public.item
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    price money,
    CONSTRAINT item_pkey PRIMARY KEY (id),
    CONSTRAINT name_unique UNIQUE (name)
)

CREATE TABLE IF NOT EXISTS public.store
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    address character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT store_pkey PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS public.sales
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    sale_time timestamp with time zone NOT NULL DEFAULT now(),
    item_id integer NOT NULL,
    store_id integer NOT NULL,
    CONSTRAINT sales_pkey PRIMARY KEY (id),
    CONSTRAINT fk_item FOREIGN KEY (item_id)
        REFERENCES public.item (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_store FOREIGN KEY (store_id)
        REFERENCES public.store (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
