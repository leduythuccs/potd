import sqlite3
import csv
import unicodedata
class PotdDBConn:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS potd_queue ('
            'link       TEXT,'
            'note       TEXT,'
            'author     TEXT'
            ')'
        )
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS potd_used ('
            'link       TEXT,'
            'note       TEXT,'
            'author     TEXT'
            ')'
        )
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS potd_using ('
            'link       TEXT,'
            'note       TEXT,'
            'author     TEXT'
            ')'
        )

        # self.conn.execute(
        #     'CREATE TABLE IF NOT EXISTS rank ('
        #     'link       TEXT,'
        #     'note       TEXT,'
        #     'author     TEXT'
        #     ')'
        # )

    def check_exists(self, table, where, value):
        query = (
            'SELECT 1 '
            'FROM {0} '.format(table) +
            'WHERE {0} = ?'.format(where)
        )
        res = self.conn.execute(query, (value, )).fetchone()
        return res is not None

    def today_potd(self):
        x = self.get_data('potd_using', limit=1)
        if len(x) == 0:
            return None
        return x[0]

    def add_potd(self, link, note, author):
        if self.check_exists('potd_queue', 'link', link) or \
                self.check_exists('potd_using', 'link', link) or \
                self.check_exists('potd_used', 'link', link):
            return False
        query = (
            'INSERT INTO potd_queue (link, note, author) '
            'VALUES (?, ?, ?)'
        )
        self.conn.execute(query, (link, note, author))
        self.conn.commit()
        return True
    def add_used_potd(self, link, note, author):
        query = (
            'INSERT INTO potd_used (link, note, author) '
            'VALUES (?, ?, ?)'
        )
        self.conn.execute(query, (link, note, author))
        self.conn.commit()
        return True
    def get_potd(self):
        x = self.get_data('potd_queue', limit=1)
        if len(x) == 0:
            return None
        return x[0]
    def move_problem(self, source_table, to_table, link, note, author):
        if self.check_exists(source_table, 'link', link):
            query = (
                f'DELETE FROM {source_table} '
                'WHERE link = ?'
            )
            self.conn.execute(query, (link,))
        query = (
            f'INSERT INTO {to_table} '
            'VALUES (?, ?, ?)'
        )
        self.conn.execute(query, (link, note, author))
        self.conn.commit()
    #for local debug
    def get_data(self, table, limit = 10):
        query = (
            'SELECT * '
            'FROM {0} '.format(table)
        )
        if limit is not None:
            query +=  'LIMIT {0}'.format(limit)
        x = self.conn.execute(query).fetchall()
        return x


PotdDB = PotdDBConn('database/potd.db')
