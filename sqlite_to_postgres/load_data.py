import os
import sqlite3
import logging
from contextlib import closing, contextmanager
from dataclasses import dataclass, astuple
from typing import Generator
from uuid import UUID
from datetime import date, datetime

import psycopg
from psycopg.rows import dict_row
import zoneinfo
from dotenv import load_dotenv

from constants import (BATCH_SIZE, LOGGER_NAME, LOGGER_FILE,
                       LOGGER_CODE, LOGGER_FORMAT,
                       FILM_WORK_FIELDS, DB_PATH, DATE_FORMAT)

load_dotenv()

db_path = DB_PATH
date_format = DATE_FORMAT


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


dsl = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
}


@dataclass
class Genre:
    id: UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)
        if isinstance(self.created_at, str):
            self.created_at = datetime.strptime(
                self.created_at, date_format
            ).replace(
                tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC')
            )
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.strptime(
                self.updated_at, date_format
            ).replace(
                tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC')
            )


@dataclass
class Person:
    id: UUID
    full_name: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)
        if isinstance(self.created_at, str):
            self.created_at = datetime.strptime(
                self.created_at, date_format
            ).replace(
                tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC')
            )
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.strptime(
                self.updated_at, date_format
            ).replace(
                tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC')
            )


@dataclass
class Filmwork:
    id: UUID
    title: str
    description: str
    creation_date: date
    rating: float
    type: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)
        if isinstance(self.creation_date, str):
            self.creation_date = date(self.creation_date)
        if isinstance(self.created_at, str):
            self.created_at = datetime.strptime(
                self.created_at, date_format
            ).replace(
                tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC')
            )
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.strptime(
                self.updated_at, date_format
            ).replace(
                tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC')
            )


@dataclass
class GenreFilmwork:
    id: UUID
    film_work_id: UUID
    genre_id: UUID
    created_at: datetime

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)
        if isinstance(self.film_work_id, str):
            self.film_work_id = UUID(self.film_work_id)
            self.genre_id = UUID(self.genre_id)
        if isinstance(self.created_at, str):
            self.created_at = datetime.strptime(
                self.created_at, date_format
            ).replace(
                tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC')
            )


@dataclass
class PersonFilmwork:
    id: UUID
    film_work_id: UUID
    person_id: UUID
    role: str
    created_at: datetime

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)
        if isinstance(self.film_work_id, str):
            self.film_work_id = UUID(self.film_work_id)
        if isinstance(self.person_id, str):
            self.person_id = UUID(self.person_id)
        if isinstance(self.created_at, str):
            self.created_at = datetime.strptime(
                self.created_at, date_format
            ).replace(
                tzinfo=zoneinfo.ZoneInfo(key='Etc/UTC')
            )


TABLE_CLASS = {
    'film_work': Filmwork,
    'genre': Genre,
    'person': Person,
    'genre_film_work': GenreFilmwork,
    'person_film_work': PersonFilmwork
}


POSTGRES_TABLES_FIELDS = {
    'film_work':
        '(id, title, description, creation_date, rating,\n'
        'type, created, modified) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
    'genre': '(id, name, description, created,\n'
    'modified) VALUES (%s, %s, %s, %s, %s)',
    'person': '(id,full_name,created,modified) VALUES (%s, %s, %s, %s)',
    'genre_film_work': '(id, film_work_id,\n'
    'genre_id, created) VALUES (%s, %s, %s, %s)',
    'person_film_work': '(id, film_work_id, person_id,\n'
    'role, created) VALUES (%s, %s, %s, %s, %s)'
}


def extract_data(
    sqlite_cursor: sqlite3.Cursor, table_name
) -> Generator[list[sqlite3.Row], None, None]:
    if table_name == 'film_work':
        sqlite_cursor.execute(f'SELECT {FILM_WORK_FIELDS} FROM {table_name};')
    else:
        sqlite_cursor.execute(f'SELECT * FROM {table_name};')
    while results := sqlite_cursor.fetchmany(BATCH_SIZE):
        yield results


def transform_data(sqlite_cursor: sqlite3.Cursor, table_name, model):
    try:
        for batch in extract_data(sqlite_cursor, table_name):
            yield [model(**dict(row)) for row in batch]
    except sqlite3.Error as exception:
        logger.error(exception)


def load_data(
    sqlite_cursor: sqlite3.Cursor, pg_cursor: psycopg.Cursor, table_name, model
):
    for batch in transform_data(sqlite_cursor, table_name, model):
        query = f'INSERT INTO content.{table_name} {POSTGRES_TABLES_FIELDS[table_name]} ON CONFLICT (id) DO NOTHING' # noqa
        batch_as_tuples = [astuple(value) for value in batch]
        pg_cursor.executemany(query, batch_as_tuples)


def test_transfer(
    sqlite_cursor: sqlite3.Cursor, pg_cursor: psycopg.Cursor, table_name, model
):
    if table_name == 'film_work':
        sqlite_cursor.execute(f'SELECT {FILM_WORK_FIELDS} FROM {table_name};')
    else:
        sqlite_cursor.execute(f'SELECT * FROM {table_name};')
    while batch := sqlite_cursor.fetchmany(BATCH_SIZE):
        original_batch = [model(**dict(row)) for row in batch]
        ids = [row.id for row in original_batch]

        pg_cursor.execute(
            f'SELECT * FROM {table_name} WHERE id = ANY(%s)', [ids]
        )
        transferred_batch = []
        for row in pg_cursor.fetchall():
            row['created_at'] = row['created']
            if 'modified' in row:
                row['updated_at'] = row['modified']
                del (row['modified'])
            del (row['created'])
            transferred_batch.append(model(**row))
        assert len(original_batch) == len(transferred_batch)
        assert sorted(
            original_batch, key=lambda d: d.id
        ) == sorted(
            transferred_batch, key=lambda d: d.id
        )


if __name__ == '__main__':
    with conn_context(
        db_path
    ) as sqlite_conn, closing(psycopg.connect(**dsl)) as pg_conn:
        logger = logging.getLogger(LOGGER_NAME)
        logging.basicConfig(
            format=LOGGER_FORMAT,
            filename=LOGGER_FILE,
            encoding=LOGGER_CODE,
            level=logging.DEBUG
        )
        logger.info('Старт чтения из sqlite и запись в postgres')
        sqlite_conn.row_factory = sqlite3.Row
        for table_name, model in TABLE_CLASS.items():
            with closing(
                sqlite_conn.cursor()
            ) as sqlite_cur, closing(
                pg_conn.cursor(row_factory=dict_row)
            ) as pg_cur:
                load_data(sqlite_cur, pg_cur, table_name, model)
                logger.info(f'Загрузка данных {table_name} выполнена!!!')
                pg_conn.commit()
                test_transfer(sqlite_cur, pg_cur, table_name, model)
                logger.info(
                    f'Тесты успешно для данных {table_name} пройдены!!!'
                )
    logger.info('🎉 Данные успешно перенесены!!!')
