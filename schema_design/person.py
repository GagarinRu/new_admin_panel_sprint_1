import random
import uuid

import psycopg

import datetime
from faker import Faker


if __name__ == '__main__':
    fake = Faker()

    # Подготавливаем DSN (Data Source Name) для подключения к БД Postgres
    dsn = {
        'dbname': 'movies_database',
        'user': 'app',
        'password': '123qwe',
        'host': 'localhost',
        'port': 5432,
        'options': '-c search_path=content',
    }

    PERSONS_COUNT = 100000

    now = datetime.datetime.now(datetime.UTC)

    with psycopg.connect(**dsn) as conn, conn.cursor() as cur:
        persons_ids = [str(uuid.uuid4()) for _ in range(PERSONS_COUNT)]
        query = 'INSERT INTO person (id, full_name, created, modified) VALUES (%s, %s, %s, %s)'
        data = [(pk, fake.last_name(), now, now) for pk in persons_ids]
        cur.executemany(query, data)
        conn.commit()

        person_film_work_data = []
        roles = ['actor', 'producer', 'director']

        cur.execute('SELECT id FROM film_work')
        film_works_ids = [data[0] for data in cur.fetchall()]

        for film_work_id in film_works_ids:
            for person_id in random.sample(persons_ids, 5):
                role = random.choice(roles)
                person_film_work_data.append((str(uuid.uuid4()), film_work_id, person_id, role, now))

        query = 'INSERT INTO person_film_work (id, film_work_id, person_id, role, created) VALUES (%s, %s, %s, %s, %s)'
        cur.executemany(query, person_film_work_data)
        conn.commit()
