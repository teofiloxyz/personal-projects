#!/usr/bin/python3
''' Fintracker (ou personal finances tracker) é um menu simples,
onde se registam todas as transações efetuadas.'''

import os
import subprocess
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from Tfuncs import gmenu, oupt


class Fintracker:
    def __init__(self):
        self.now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.now_strp = datetime.strptime(self.now, '%Y-%m-%d %H:%M:%S')

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
    def show_transactions(self, option, timespan):
        if option == 'all':
            self.df = pd.read_sql('SELECT * FROM transactions LEFT JOIN '
                                  'expenses USING(transaction_id)',
                                  self.db_con)
        elif option == 'expenses':
            self.df = pd.read_sql('SELECT * FROM transactions LEFT JOIN '
                                  'expenses USING(transaction_id) WHERE '
                                  'trn_type = "Expense"',
                                  self.db_con)
        elif option == 'revenue':
            self.df = pd.read_sql('SELECT * FROM transactions WHERE '
                                  'trn_type = "Revenue"',
                                  self.db_con)

        if type(timespan) != 'int':
            try:
                timespan = int(timespan)
            except ValueError:
                print('Must enter an integer...')
                return

        date_limit = datetime.strftime(self.now_strp
                                       - timedelta(days=timespan),
                                       '%Y-%m-%d %H:%M:%S')
        df = self.df.loc[self.df['time'] > date_limit]
        print(df.to_string(index=False))

    @generic_connection
    def summary(self):
        df = pd.read_sql('SELECT * FROM transactions', self.db_con)
        date_24h = datetime.strftime(self.now_strp - timedelta(days=1),
                                     '%Y-%m-%d %H:%M:%S')
        date_7d = datetime.strftime(self.now_strp - timedelta(days=7),
                                    '%Y-%m-%d %H:%M:%S')
        date_30d = datetime.strftime(self.now_strp - timedelta(days=30),
                                     '%Y-%m-%d %H:%M:%S')

        revenue_24h = df[(df['time'] > date_24h)
                         & (df['trn_type'] == 'Revenue')].sum().amount
        expenses_24h = df[(df['time'] > date_24h)
                          & (df['trn_type'] == 'Expense')].sum().amount
        balance_24h = revenue_24h - expenses_24h

        revenue_7d = df[(df['time'] > date_7d)
                        & (df['trn_type'] == 'Revenue')].sum().amount
        expenses_7d = df[(df['time'] > date_7d)
                         & (df['trn_type'] == 'Expense')].sum().amount
        balance_7d = revenue_7d - expenses_7d

        revenue_30d = df[(df['time'] > date_30d)
                         & (df['trn_type'] == 'Revenue')].sum().amount
        expenses_30d = df[(df['time'] > date_30d)
                          & (df['trn_type'] == 'Expense')].sum().amount
        balance_30d = revenue_30d - expenses_30d

        values = {'Revenue': [revenue_24h, revenue_7d, revenue_30d],
                  'Expenses': [expenses_24h, expenses_7d, expenses_30d],
                  'Balance': [balance_24h, balance_7d, balance_30d]}
        timespan = ['last 24 hours', 'last 7 days', 'last 30 days']
        print(pd.DataFrame(data=values, index=timespan))

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
        def remove(trn_id):
            try:
                trn_id = int(trn_id)
            except ValueError:
                print('Must enter an integer...')
                return False

            self.cursor.execute('SELECT * FROM transactions WHERE '
                                f'transaction_id = {trn_id}')
            trn_id_fetch = self.cursor.fetchone()
            if trn_id_fetch is None:
                print(f"Transaction with id '{trn_id}' not found on database!")
                return False

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
                print(f"Database error! Transaction with id '{trn_id}' was "
                      "not removed!")
            return True

        self.df = pd.read_sql('SELECT * FROM transactions LEFT JOIN expenses '
                              'USING(transaction_id)',
                              self.db_con)
        print(self.df.to_string(index=False))
        while True:
            selected_id = input('\nEnter the transaction_id to remove or '
                                'several (e.g.: 30+4+43): ')
            if selected_id == 'q':
                print('Aborting...')
                return
            elif '+' in selected_id:
                selected_id = selected_id.split('+')
                no_errors = [remove(trn_id) for trn_id in selected_id]
            else:
                no_errors = remove(selected_id)
            if no_errors:
                break

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
keys = {'ls': (lambda timespan=30: ft.show_transactions('all', timespan),
               "show past # (default 30) days transactions"),
        'lse': (lambda timespan=30: ft.show_transactions('expenses', timespan),
                "show past # (default 30) days expenses"),
        'lsr': (lambda timespan=30: ft.show_transactions('revenue', timespan),
                "show past # (default 30) days revenue"),
        'lt': (ft.summary,
               "show summary"),
        'ad': (ft.add_transaction,
               "add transaction to database"),
        'rm': (ft.remove_transaction,
               "remove transaction from database"),
        'ex': (ft.export_to_csv,
               "export database tables to CSV file")}
extra_func = ft.summary
gmenu(title, keys, extra_func)
