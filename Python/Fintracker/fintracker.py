#!/usr/bin/python3
''' Fintracker (ou personal finances tracker) é um menu simples,
onde se registam todas as transações efetuadas.'''

import sqlite3
import pandas as pd
from datetime import datetime
from Tfuncs import gmenu


class Fintracker:
    def __init__(self):
        self.database_path = 'fintracker.db'
        self.db_table = 'transactions'
        self.now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.now_strp = datetime.strptime(self.now, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def generic_connection(func):
        def process(self, *args, **kwargs):
            self.db_con = sqlite3.connect(self.db_path)
            self.cursor = self.db_con.cursor()
            func(self, *args, **kwargs)
            self.db_con.close()
        return process

    @generic_connection
    def show_transactions(self):
        self.df = pd.read_sql(f'SELECT * FROM {self.db_table}', self.db_con)
        print(self.df.to_string())

    @generic_connection
    def add_transaction(self):
        while True:
            amount = input('Enter amount of transaction (e.g.: 100.5): ')
            if amount == 'q':
                print('Aborting...')
                return
            try:
                amount = float(amount)
            except ValueError:
                print('Value error, try again: ')
                continue
            break

        category = input('Enter category: ')
        if category == 'q':
            print('Aborting...')
            return

        note = input('Enter a note (leave empty for none): ')
        if note == 'q':
            print('Aborting...')
            return

        entry = self.now, amount, category, note
        self.cursor.execute(f'INSERT INTO {self.db_table} (time, amount, '
                            f'category, note) VALUES {entry}')
        self.db_con.commit()

        self.cursor.execute(f'SELECT * FROM {self.db_table} ORDER BY '
                            'rowid DESC LIMIT 1')
        last = self.cursor.fetchall()
        if last == [entry]:
            print('Entry successfuly saved on database!')
        else:
            print('Database error! Entry not saved!')


ft = Fintracker()
title = 'Fintracker-Menu'
keys = {'ls': (ft.show_transactions,
               "show past 30 days transactions"),
        'ad': (ft.add_transaction,
               "add transaction to database")}
gmenu(title, keys)
