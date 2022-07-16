#!/usr/bin/python3
''' Fintracker (ou personal finances tracker) é um menu simples,
onde se registam todas as transações efetuadas.
Também guarda o balanço, e é possível editá-lo.'''

import os
import subprocess
import json
import sqlite3
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from Tfuncs import gmenu, oupt, fcol, ffmt


class Fintracker:
    def __init__(self):
        self.now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.now_strp = datetime.strptime(self.now, '%Y-%m-%d %H:%M:%S')
        self.message = list()

        with open('config.json', 'r') as cf:
            self.json_info = json.load(cf)

        self.db_path = self.json_info['db_path']

        if not os.path.isfile(self.db_path):
            self.setup_database()

        self.auto_transactions()

    def opening_message(self):
        if len(self.message) != 0:
            print(f"{fcol.red}{ffmt.bold}New Message:{ffmt.reset}")
            print("\n".join(self.message))
            print()

        need_to_edit_balance = False
        # Ñ dou merge aos dicionários pq podem ter items com o mesmo nome
        balance = self.json_info['assets'].items(), \
            self.json_info['liabilities'].items()
        for items in balance:
            for item, amount in items:
                if amount < 0:
                    need_to_edit_balance = True
                    print(f'{ffmt.bold}{fcol.red}{item.capitalize()} '
                          f'is negative!{ffmt.reset}')

        if need_to_edit_balance:
            print(f'{ffmt.bold}{fcol.red}Please edit the balance '
                  f'statement!{ffmt.reset}\n')

        self.summary()

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

    def save_json(self):
        with open('config.json', 'w') as cf:
            json.dump(self.json_info, cf)

    @staticmethod
    def generic_connection(func):
        def process(self, *args, **kwargs):
            self.db_con = sqlite3.connect(self.db_path)
            self.cursor = self.db_con.cursor()
            func(self, *args, **kwargs)
            self.db_con.close()
        return process

    @generic_connection
    def auto_transactions(self):
        # Posso adicionar expenses também
        for n, income in enumerate(self.json_info['incomes'].values(), 1):
            date = income['expected_date']
            date_strp = datetime.strptime(date, '%Y-%m-%d')
            amount = income['expected_amount']
            income_title = income['title']
            if self.now_strp >= date_strp:
                entry = self.now, 'Revenue', amount, income_title
                self.cursor.execute('INSERT INTO transactions (time, '
                                    f'trn_type, amount, note) VALUES {entry}')
                self.db_con.commit()

                if income['recurrence'] == 'monthly':
                    delta = relativedelta(months=1)
                else:
                    delta = timedelta(days=7)
                new_date = datetime.strftime(date_strp + delta, '%Y-%m-%d')
                self.json_info['incomes'][str(n)]['expected_date'] = new_date
                # O dinheiro ganho aumenta a rúbrica cash do balanço
                self.json_info['assets']['cash'] += amount
                self.save_json()

                amount_eur = "€ {:,.2f}".format(amount)
                self.message.append(f"{amount_eur} from {income_title} "
                                    "was added!")

    @generic_connection
    def show_transactions(self, option, timespan):
        if option == 'all':
            df = pd.read_sql('SELECT * FROM transactions LEFT JOIN '
                             'expenses USING(transaction_id)', self.db_con)
        elif option == 'expenses':
            df = pd.read_sql('SELECT * FROM transactions LEFT JOIN '
                             'expenses USING(transaction_id) WHERE '
                             'trn_type = "Expense"', self.db_con)
        elif option == 'revenue':
            df = pd.read_sql('SELECT * FROM transactions WHERE '
                             'trn_type = "Revenue"', self.db_con)

        if type(timespan) != 'int':
            try:
                timespan = int(timespan)
            except ValueError:
                print('Must enter an integer...')
                return

        date_limit = datetime.strftime(self.now_strp
                                       - timedelta(days=timespan),
                                       '%Y-%m-%d %H:%M:%S')
        df = df.loc[df['time'] > date_limit]
        print(df.to_string(index=False))

    @generic_connection
    def show_balance(self):
        assets = self.json_info['assets']
        assets_sum = sum(assets.values())
        liabilities = self.json_info['liabilities']
        liabilities_sum = sum(liabilities.values())
        balance = assets_sum - liabilities_sum

        print(f"{ffmt.bold}{fcol.green}Assets:{ffmt.reset} "
              f"{'€ {:,.2f}'.format(assets_sum)}")
        [print(f"{asset.capitalize()}: {'€ {:,.2f}'.format(amount)}")
         for asset, amount in assets.items()]

        print(f"\n{ffmt.bold}{fcol.red}Liabilities:{ffmt.reset} "
              f"{'€ {:,.2f}'.format(liabilities_sum)}")
        [print(f"{liability.capitalize()}: {'€ {:,.2f}'.format(amount)}")
         for liability, amount in liabilities.items()]

        print(f"\n{ffmt.bold}{fcol.yellow}Balance:{ffmt.reset} "
              f"{'€ {:,.2f}'.format(balance)}")

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
        timespan = ['Last 24 hours', 'Last 7 days', 'Last 30 days']
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
            categories = self.json_info['expenses_categories']
            [print(f"[{n}] {category}")
             for n, category in enumerate(categories, 1)]
            while True:
                category = input('\nEnter category # (or enter '
                                 'custom name): ').capitalize()
                if category in ('Q', ''):
                    print('Aborting...')
                    return
                elif category in categories:
                    print('Category already in list...')
                else:
                    try:
                        category = categories[int(category) - 1]
                        break
                    except IndexError:
                        print('Index outside the list...')
                    except ValueError:
                        self.json_info['expenses_categories'].append(category)
                        self.save_json()
                        break

        note = input('Enter a note (leave empty for none): ')
        if note == 'q':
            print('Aborting...')
            return

        if trn_type == "Expense":
            self.json_info['assets']['cash'] -= amount
        else:
            self.json_info['assets']['cash'] += amount
        self.save_json()

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

        if self.json_info['assets']['cash'] < 0:
            print(f'{ffmt.bold}{fcol.red}You got negative cash, please edit '
                  f'the balance statement!{ffmt.reset}')

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

            trn_type, amount, note = \
                trn_id_fetch[2], trn_id_fetch[3], trn_id_fetch[4]

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
                # Correct the balance statement
                if trn_type == 'Balance':
                    def change_balance_item(entry):
                        category = 'assets' if entry[1] == 'a' \
                            else 'liabilities'
                        item = entry[3:]
                        operation = entry[0]

                        item_val = self.json_info[category][item] if item \
                            in self.json_info[category].keys() else 0
                        if operation == '+':
                            # Reversed bc removed transaction
                            self.json_info[category][item] = item_val - amount
                        else:
                            self.json_info[category][item] = item_val + amount

                    note_1 = re.sub(' [-+][la]:.*$', "", note)
                    note_2 = note.replace(note_1, "").strip()

                    change_balance_item(note_1)
                    # if not isolated balance change to be reversed
                    if note_2 != '':
                        change_balance_item(note_2)

                elif trn_type == 'Expense':
                    self.json_info['assets']['cash'] += amount
                else:
                    self.json_info['assets']['cash'] -= amount
                self.save_json()
            else:
                print(f"Database error! Transaction with id '{trn_id}' was "
                      "not removed!")
            return True

        df = pd.read_sql('SELECT * FROM transactions LEFT JOIN expenses '
                         'USING(transaction_id)', self.db_con)
        print(df.to_string(index=False))
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

        need_to_edit_balance = False
        # Ñ dou merge aos dicionários pq podem ter items com o mesmo nome
        balance = self.json_info['assets'].items(), \
            self.json_info['liabilities'].items()
        for items in balance:
            for item, amount in items:
                if amount < 0:
                    need_to_edit_balance = True
                    print(f'{ffmt.bold}{fcol.red}{item.capitalize()} '
                          f'is negative!{ffmt.reset}')

        if need_to_edit_balance:
            print(f'{ffmt.bold}{fcol.red}Please edit the balance '
                  f'statement!{ffmt.reset}')

    # Needs refactoring
    @generic_connection
    def edit_balance(self):
        def pick_balance_item(question, can_cancel=False):
            while True:
                items_list, n = list(), 1
                for items in balance.items():
                    print(f"\n{items[0].capitalize()}: ")
                    for item in items[1]:
                        print(f"[{n}] {item.capitalize()}")
                        items_list.append(item)
                        n += 1
                    singular = 'asset' if items[0] == 'assets' else 'liability'
                    print(f"[{n}] Create new {singular}")
                    items_list.append('create new')
                    n += 1

                selection = input(f"\n{question}")
                if selection == 'q':
                    print("Aborting...")
                    return
                elif selection == '' and can_cancel:
                    return None, None
                try:
                    selection = int(selection)
                except ValueError:
                    print("Pick a number...")
                    continue

                if 0 < selection <= len(items_list):
                    # len assets + 1 por causa do create new
                    if selection <= len(balance['assets']) + 1:
                        category = 'assets'
                    else:
                        category = 'liabilities'

                    item = items_list[selection - 1]

                    if item == "create new":
                        while True:
                            singular = 'asset' if category == 'assets' \
                                else 'liability'
                            item = input('Enter name for the new '
                                         f'{singular}: ').lower()
                            if item == 'q':
                                print("Aborting...")
                                return
                            elif item in self.json_info[category].keys():
                                if category == 'assets':
                                    print("There's already an asset named "
                                          f"{item}")
                                else:
                                    print("There's already a liability "
                                          f"named {item}")
                                continue
                            break
                        balance[category][item] = 0

                    return (category, item)

        # dict para fazer uma cópia
        balance = {'assets': dict(self.json_info['assets']),
                   'liabilities': dict(self.json_info['liabilities'])}

        try:
            category, item = pick_balance_item("Choose the item to edit: ")
        except TypeError:
            return

        item_val = balance[category][item]
        print(f"Current value of {item.capitalize()}: {item_val}")

        while True:
            new_item_val = input("Enter the new value for "
                                 f"{item.capitalize()}: ")
            if new_item_val == 'q':
                print('Aborting...')
                return
            try:
                new_item_val = float(new_item_val)
            except ValueError:
                print('Must be a number...')
                continue
            if new_item_val < 0:
                print('Cannot be negative!')
                continue
            break

        del balance[category][item]

        val_diff = round(new_item_val - item_val, 2)
        if (val_diff > 0 and category == 'assets') \
                or (val_diff < 0 and category != 'assets'):
            ast_operation, lib_operation = 'subtract', 'add'
        else:
            ast_operation, lib_operation = 'add', 'subtract'

        description = '-' if val_diff < 0 else '+'
        description += f"{category[0]}:{item}"

        val_diff = abs(val_diff)
        ast_operation += f" € {val_diff}"
        lib_operation += f" € {val_diff}"

        while True:
            try:
                category_2, item_2 = \
                    pick_balance_item(f"Choose an asset to {ast_operation} or "
                                      f"liability to {lib_operation}, or "
                                      "leave empty if is isolated: ",
                                      can_cancel=True)
            except TypeError:
                return

            if category_2 is None:
                break

            item_2_val = balance[category_2][item_2]
            if category_2 == 'assets':
                if ast_operation.startswith('subtract'):
                    new_item_2_val = item_2_val - val_diff
                    description += f" -a:{item_2}"
                else:
                    new_item_2_val = item_2_val + val_diff
                    description += f" +a:{item_2}"
            else:
                if lib_operation.startswith('subtract'):
                    new_item_2_val = item_2_val - val_diff
                    description += f" -l:{item_2}"
                else:
                    new_item_2_val = item_2_val + val_diff
                    description += f" +l:{item_2}"

            if new_item_2_val < 0:
                print(f"{item_2.capitalize()} can't become negative..."
                      "\nChoose another item, or cancel by entering [q]")
                continue
            break

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = now, 'Balance', val_diff, description
        self.cursor.execute('INSERT INTO transactions (time, '
                            f'trn_type, amount, note) VALUES {entry}')
        self.db_con.commit()

        self.json_info[category][item] = new_item_val
        if category_2 is not None:
            self.json_info[category_2][item_2] = new_item_2_val
        self.save_json()

    @generic_connection
    def show_charts(self):
        def time_chart_by_trn_type(trn_type):
            print(f'Showing {trn_type} chart...')
            df = pd.read_sql('SELECT SUBSTR(time, 1, 10) as date, amount FROM '
                             f'transactions WHERE trn_type = "{trn_type}"',
                             self.db_con)
            date_limit = datetime.strftime(self.now_strp - timedelta(days=30),
                                           '%Y-%m-%d')
            df = df.loc[df['date']
                        > date_limit].groupby('date')['amount'].sum()

            df.plot(x='date', y='amount', kind='line')
            plt.legend(title=trn_type)
            plt.show()

        def pie_chart_expenses_cat():
            df = pd.read_sql('SELECT SUBSTR(time, 1, 10) as date, amount, '
                             'category FROM transactions LEFT JOIN expenses '
                             'USING(transaction_id) WHERE '
                             'trn_type = "Expense"', self.db_con)
            date_limit = datetime.strftime(self.now_strp - timedelta(days=30),
                                           '%Y-%m-%d')
            df = df.loc[df['date'] > date_limit]
            categories_list = df['category'].unique().tolist()
            amounts_list = list()
            for category in categories_list:
                amount = df.loc[df['category'] == category]['amount'].sum()
                amounts_list.append(amount)

            plt.pie(np.array(amounts_list),
                    labels=categories_list,
                    autopct='%1.1f%%')
            plt.show()

        plt.style.use('dark_background')
        options = {'1': ('Revenue of last 30 days',
                         lambda: time_chart_by_trn_type('Revenue')),
                   '2': ('Expenses of last 30 days',
                         lambda: time_chart_by_trn_type('Expense')),
                   '3': ('Category percentage of expenses of last 30 days',
                         pie_chart_expenses_cat)}
        while True:
            [print(f"[{n}] {option[0]}") for n, option in options.items()]
            selection = input("\nEnter the chart option: ")
            if selection == 'q':
                print('Aborting...')
                return
            try:
                options[selection][1]()
                break
            except KeyError:
                continue

    @generic_connection
    def export_to_csv(self):
        df = pd.read_sql('SELECT * FROM transactions LEFT JOIN expenses '
                         'USING(transaction_id)', self.db_con)

        csv_out = oupt.files(question='Enter the path to save the csv file: ',
                             extension='csv', output_name='fintracker_table')
        if csv_out == 'q':
            print('Aborted...')
            return

        df.to_csv(str(csv_out), encoding='utf-8', index=False)

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
        'lsb': (ft.show_balance,
                "show balance statement"),
        'sm': (ft.summary,
               "show summary"),
        'ad': (ft.add_transaction,
               "add transaction to database"),
        'rm': (ft.remove_transaction,
               "remove transaction from database"),
        'ed': (ft.edit_balance,
               "edit balance statement"),
        'ch': (ft.show_charts,
               "select and show charts"),
        'ex': (ft.export_to_csv,
               "export database tables to CSV file")}
extra_func = ft.opening_message
gmenu(title, keys, extra_func)
