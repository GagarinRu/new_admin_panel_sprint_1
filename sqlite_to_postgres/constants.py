BATCH_SIZE = 100
LOGGER_NAME = 'Logger'
LOGGER_FILE = '.\\sqlite_to_postgres\\logger.log'
LOGGER_CODE = 'utf-8'
LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
FILM_WORK_FIELDS = (
    'id, title, description, creation_date,\n'
    'rating, type, created_at, updated_at'
)
DB_PATH = '.\\sqlite_to_postgres\\db.sqlite'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f+00'