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
        self.now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ow_strp = datetime.strptime(self.now, '%Y-%m-%d %H:%M:%S')

        self.db_path = 'fintracker.db'

        if not os.path.isfile(self.db_path):
            self.setup_database()

    def setup_database(self):
        subprocess.run(['touch', self.db_path])

        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()

        self.cursor.execute('CREATE TABLE transactions(transaction_id '
                            'INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL '
                            'UNIQUE, time TEXT NOT NULL, trn_type TEXT '
                            'NOT NULL, amount REAL NOT NULL, note TEXT)')
        # Eu sei que podia ficar tudo numa tabela com category NULL
        self.cursor.execute('CREATE TABLE expenses(transaction_id '
                            'INTEGER, category TEXT NOT NULL, '
                            'FOREIGN KEY(transaction_id) '
                            'REFERENCES transactions(transaction_id))')
        self.db_con.commit()

        self.db_con.close()

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
        self.df = pd.read_sql('SELECT * FROM transactions LEFT JOIN expenses '
                              'USING(transaction_id)',
                              self.db_con)
        print(self.df.to_string(index=False))

    @generic_connection
    def add_transaction(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        while True:
            amount = input('Enter amount of the expense (e.g.: 100.55 or '
                           '+100.55 if revenue): ')
            if amount == 'q':
                print('Aborting...')
                return
            if amount.startswith('-'):
                continue
            # Most of the transactions will be expenses
            trn_type = 'Revenue' if amount.startswith('+') else 'Expense'
            try:
                amount = round(float(amount), 2)
            except ValueError:
                print('Value error, try again: ')
                continue
            break

        if trn_type == 'Expense':
            # Select between categories of enter custom
            category = input('Enter category: ')
            if category == 'q':
                print('Aborting...')
                return

        note = input('Enter a note (leave empty for none): ')
        if note == 'q':
            print('Aborting...')
            return

        entry = now, trn_type, amount, note
        self.cursor.execute('INSERT INTO transactions (time, trn_type, '
                            f'amount, note) VALUES {entry}')
        self.db_con.commit()

        self.cursor.execute('SELECT * FROM transactions ORDER BY '
                            'transaction_id DESC LIMIT 1')
        last = self.cursor.fetchone()
        if last[1:] == entry:
            print('Transaction successfuly saved on database!')
        else:
            print('Database error! Transaction not saved!')

        if trn_type == 'Expense':
            trn_id = last[0]
            self.cursor.execute('INSERT INTO expenses (transaction_id, '
                                f'category) VALUES {trn_id, category}')
            self.db_con.commit()

    @generic_connection
    def remove_transaction(self):
        self.df = pd.read_sql('SELECT * FROM transactions LEFT JOIN expenses '
                              'USING(transaction_id)',
                              self.db_con)
        print(self.df.to_string(index=False))
        while True:
            trn_id = input('\nEnter the transaction_id to remove: ')
            if trn_id == 'q':
                print('Aborting...')
                return
            try:
                trn_id = int(trn_id)
            except ValueError:
                print('Must enter an integer...')
                continue
            self.cursor.execute('SELECT * FROM transactions WHERE '
                                f'transaction_id = {trn_id}')
            trn_id_fetch = self.cursor.fetchone()
            if trn_id_fetch is None:
                print(f"Transaction with id '{trn_id}' not found on database!")
                continue
            break

        self.cursor.execute('DELETE FROM transactions WHERE '
                            f'transaction_id = {trn_id}')
        if trn_id_fetch[2] == 'Expense':
            self.cursor.execute('DELETE FROM expenses WHERE '
                                f'transaction_id = {trn_id}')
        self.db_con.commit()

        self.cursor.execute('SELECT * FROM transactions WHERE '
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
        self.df = pd.read_sql('SELECT * FROM transactions LEFT JOIN expenses '
                              'USING(transaction_id)',
                              self.db_con)

        csv_out = oupt.files(question='Enter the path to save the csv file: ',
                             extension='csv', output_name='fintracker_table')
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
               "export database tables to CSV file")}
gmenu(title, keys)
