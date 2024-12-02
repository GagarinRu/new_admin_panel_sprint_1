import os
import random
import uuid

import psycopg
from dotenv import load_dotenv
import datetime
from faker import Faker


load_dotenv()

if __name__ == '__main__':
    fake = Faker()

    dsn = {
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
        'options': os.getenv('POSTGRES_OPTION'),
    }

    PERSONS_COUNT = 100000

    now = datetime.datetime.now(datetime.timezone.utc)

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
