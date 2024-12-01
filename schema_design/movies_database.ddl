CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);


CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    created timestamp with time zone,
	CONSTRAINT fk_genre_id
        FOREIGN KEY (genre_id)
        REFERENCES genre (id)
        ON DELETE CASCADE,
	CONSTRAINT fk_film_work_id
        FOREIGN KEY (film_work_id)
        REFERENCES film_work (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role TEXT NOT NULL,
    created timestamp with time zone,
	CONSTRAINT fk_person_id
        FOREIGN KEY (person_id)
        REFERENCES person (id)
        ON DELETE CASCADE,
	CONSTRAINT fk_film_work_id
        FOREIGN KEY (film_work_id)
        REFERENCES film_work (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS person_full_name_idx ON person (full_name);
CREATE INDEX IF NOT EXISTS film_work_title_idx ON film_work (title);
CREATE INDEX IF NOT EXISTS genre_name_idx ON genre (name);
CREATE UNIQUE INDEX IF NOT EXISTS person_film_work_role_idx ON person_film_work (film_work_id, person_id, role);
CREATE UNIQUE INDEX IF NOT EXISTS genre_film_work_idx ON genre_film_work (genre_id, film_work_id);




