import psycopg2
import psycopg2.errors
from typing import List, Tuple, Optional

from .settings import *


class Connection:
    def __init__(self, *,
                 host: Optional[str] = None,
                 database: Optional[str] = None,
                 port: Optional[str] = None,
                 user: Optional[str] = None,
                 password: Optional[str] = None,
                 create_database: bool = False,
                 ) -> None:
        self.host: str = host or POSTGRES_HOST
        self.database: str = database or POSTGRES_DATABASE
        self.port: str = port or POSTGRES_PORT
        self.user: str = user or POSTGRES_USER
        self.password: str = password or POSTGRES_PASSWORD

        if create_database:
            self._create_database()

        self._connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def close(self) -> None:
        self._connection.close()

    def insert(self, *, title: str, url: str) -> None:
        with self._connection.cursor() as curs:
            curs.execute(r'INSERT INTO ads (title, url) VALUES (%s, %s);', (title, url))
        self._connection.commit()

    def make_table(self, clear: bool = False):
        with self._connection.cursor() as curs:
            curs.execute(
                r'''
                CREATE TABLE IF NOT EXISTS ads (
                    id serial PRIMARY KEY,
                    title text,
                    url text
                    );
                '''
            )

            if clear:
                curs.execute(r'DELETE FROM ads; ')

        self._connection.commit()

    def select_table(self) -> List[Tuple[str, str]]:
        with self._connection.cursor() as curs:
            curs.execute(r'SELECT title, url FROM ads;')
            return curs.fetchall()

    def healthcheck(self) -> bool:
        raise NotImplementedError('')

    def _create_database(self) -> None:
        connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password
        )
        connection.autocommit = True

        try:
            with connection.cursor() as curs:
                try:
                    curs.execute(f'''CREATE DATABASE {self.database};''')
                except psycopg2.errors.DuplicateDatabase:
                    pass
        finally:
            connection.close()
