#!/usr/bin/python3
''' Fintracker (ou personal finances tracker) é um menu simples,
onde se registam todas as transações efetuadas.'''

import os
import subprocess
import sqlite3
import pandas as pd
from datetime import datetime
from Tfuncs import gmenu, oupt


class Fintracker:
    def __init__(self):
        self.db_path = 'fintracker.db'
        self.db_table = 'transactions'
        self.now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.now_strp = datetime.strptime(self.now, '%Y-%m-%d %H:%M:%S')
        if not os.path.isfile(self.db_path):
            self.setup_database()

    @staticmethod
    def generic_connection(func):
        def process(self, *args, **kwargs):
            self.db_con = sqlite3.connect(self.db_path)
            self.cursor = self.db_con.cursor()
            func(self, *args, **kwargs)
            self.db_con.close()
        return process

    def setup_database(self):
        subprocess.run(['touch', self.db_path])
        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()
        self.cursor.execute(f'CREATE TABLE {self.db_table}(transaction_id '
                            'INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL '
                            'UNIQUE, time TEXT NOT NULL, trn_type TEXT '
                            'NOT NULL, amount REAL NOT NULL, category TEXT '
                            'NOT NULL, note TEXT)')
        self.db_con.commit()
        self.db_con.close()

    @generic_connection
    def show_transactions(self):
        self.df = pd.read_sql(f'SELECT * FROM {self.db_table}', self.db_con)
        print(self.df.to_string())

    @generic_connection
    def add_transaction(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # now_strp = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')

        while True:
            amount = input('Enter amount of the cost (e.g.: 100.55 or '
                           '+100.55 if revenue): ')
            if amount == 'q':
                print('Aborting...')
                return
            # Most of the transactions will be expenses
            trn_type = 'Revenue' if amount.startswith('+') else 'Expense'
            try:
                amount = round(float(amount), 2)
            except ValueError:
                print('Value error, try again: ')
                continue
            break

        # In the future, add option: select between categories of enter custom
        category = input('Enter category: ')
        if category == 'q':
            print('Aborting...')
            return

        note = input('Enter a note (leave empty for none): ')
        if note == 'q':
            print('Aborting...')
            return

        entry = now, trn_type, amount, category, note
        self.cursor.execute(f'INSERT INTO {self.db_table} (time, trn_type, '
                            f'amount, category, note) VALUES {entry}')
        self.db_con.commit()

        self.cursor.execute(f'SELECT * FROM {self.db_table} ORDER BY '
                            'transaction_id DESC LIMIT 1')
        last = self.cursor.fetchone()[1:]
        if last == entry:
            print('Transaction successfuly saved on database!')
        else:
            print('Database error! Transaction not saved!')

    @generic_connection
    def remove_transaction(self):
        self.df = pd.read_sql(f'SELECT * FROM {self.db_table}', self.db_con)
        print(self.df.to_string(index=False))
        while True:
            try:
                trn_id = int(input('\nEnter the transaction_id to remove: '))
            except ValueError:
                print('Must enter an integer...')
                continue
            self.cursor.execute(f'SELECT * FROM {self.db_table} WHERE '
                                f'transaction_id = {trn_id}')
            trn_id_fetch = self.cursor.fetchone()
            if trn_id_fetch is None:
                print(f"Transaction with id '{trn_id}' not found on database!")
                continue
            break

        self.cursor.execute(f'DELETE FROM {self.db_table} WHERE '
                            f'transaction_id = {trn_id}')
        self.db_con.commit()

        self.cursor.execute(f'SELECT * FROM {self.db_table} WHERE '
                            f'transaction_id = {trn_id}')
        trn_id_fetch = self.cursor.fetchone()
        if trn_id_fetch is None:
            print(f"Transaction with id '{trn_id}' successfuly removed "
                  "from database!")
        else:
            print(f"Database error! Transaction with id '{trn_id}' was not "
                  "removed!")

    @generic_connection
    def export_to_csv(self):
        self.df = pd.read_sql(f'SELECT * FROM {self.db_table}', self.db_con)

        csv_out = oupt.files(question='Enter the path to save the csv file: ',
                             extension='csv', output_name=self.db_table)
        if csv_out == 'q':
            print('Aborted...')
            return

        self.df.to_csv(str(csv_out), encoding='utf-8', index=False)

        if os.path.exists(csv_out):
            print(f"Export done successfuly\nOutput at '{csv_out}'")
        else:
            print('Error, something went wrong exporting to CSV')


ft = Fintracker()
title = 'Fintracker-Menu'
keys = {'ls': (ft.show_transactions,
               "show past 30 days transactions"),
        'ad': (ft.add_transaction,
               "add transaction to database"),
        'rm': (ft.remove_transaction,
               "remove transaction from database"),
        'ex': (ft.export_to_csv,
               "export database table to CSV file")}
gmenu(title, keys)
