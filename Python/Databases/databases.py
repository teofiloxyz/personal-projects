#!/usr/bin/python3

import os
import sqlite3
import subprocess
import pandas as pd
from configparser import ConfigParser
from Tfuncs import gmenu, ffmt, fcol, qst, inpt, oupt


class Databases:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.databases_path = self.config['GENERAL']['databases_path']

    def refresh_dbs(self):
        self.dbs_opts, self.tabs_opts, self.dbs_opts_info, \
            self.tabs_opts_info,  n_db, n_tab = {}, {}, '', '', 1, 1

        for root_dirs_files in os.walk(self.databases_path):
            for file in root_dirs_files[2]:

                if file.endswith('.db'):
                    db_path = os.path.join(root_dirs_files[0], file)
                    db_name = os.path.basename(db_path)
                    self.dbs_opts[str(n_db)] = db_path
                    self.dbs_opts_info += (f'[{n_db}]: {db_name}\n')
                    n_db += 1
                    tables = str(subprocess.run(['sqlite3', db_path,
                                                 '.tables'],
                                                stdout=subprocess.PIPE)
                                 .stdout)[2:-3]

                    if ' ' in tables:
                        tables = tables.split()
                        for table in tables:
                            self.tabs_opts[str(n_tab)] = (db_path, table)
                            self.tabs_opts_info += (f'[{n_tab}]: {table} '
                                                    f'from {db_name}\n')
                            n_tab += 1
                    else:
                        self.tabs_opts[str(n_tab)] = (db_path, tables)
                        self.tabs_opts_info += (f'[{n_tab}]: {tables} '
                                                f'from {db_name}\n')
                        n_tab += 1

    def choose_db(self):
        self.db_path = qst.opts(question=f'{self.dbs_opts_info}q: quit to '
                                f'main menu\n\n{ffmt.bold}{fcol.yellow}'
                                f'Choose the database: {ffmt.reset}',
                                opts_dict=self.dbs_opts)
        if self.db_path == 'q':
            print('Aborted...')
            return False

        self.db_name = os.path.basename(self.db_path)

    def choose_db_tab(self):
        tab = qst.opts(question=f'{self.tabs_opts_info}q: quit to main '
                       f'menu\n\n{ffmt.bold}{fcol.yellow}Choose the table: '
                       f'{ffmt.reset}', opts_dict=self.tabs_opts)
        if tab == 'q':
            print('Aborted...')
            return False

        self.db_path = tab[0]
        self.db_table = tab[1]
        self.db_name = os.path.basename(self.db_path)

    def connect_to_db(self):
        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()

    def disconnect_from_db(self):
        self.db_con.close()

    def df_from_db_tab(self):
        self.df = pd.read_sql(f'SELECT * FROM {self.db_table}', self.db_con)
        self.df_output = self.df.to_string()

    @staticmethod
    def generic_connection(show_only_dbs=False):
        def decorator(func):
            def process(self):
                self.refresh_dbs()

                if show_only_dbs is False:
                    if self.choose_db_tab() is False:
                        return
                else:
                    if self.choose_db() is False:
                        return

                self.connect_to_db()
                func(self)
                self.disconnect_from_db()
            return process
        return decorator

    @generic_connection(show_only_dbs=False)
    def show_db_tab(self):
        self.df_from_db_tab()
        print(f'{ffmt.bold}{fcol.green}{self.db_table.capitalize()} from '
              f'{self.db_name.capitalize()}:{ffmt.reset}\n{self.df_output}')

    @generic_connection(show_only_dbs=False)
    def add_entry_to_db_tab(self):
        self.cursor.execute(f'pragma table_info({self.db_table})')
        columns = self.cursor.fetchall()
        entry = []

        for column in columns:
            column_name = column[1]
            column_type = column[2]
            column_entry = input(f"Enter the entry for "
                                 f"{column_name} ({column_type}): ")

            if column_type == 'INTEGER':
                column_entry = int(column_entry)
            elif column_type == 'REAL':
                column_entry = float(column_entry)
            entry.append(column_entry)

        # Tem que ser tuple
        entry = tuple(entry)
        self.cursor.execute(f'INSERT INTO {self.db_table} VALUES {entry}')
        self.db_con.commit()
        self.cursor.execute(f'SELECT * FROM {self.db_table} '
                            f'WHERE rowid=(SELECT max(rowid) '
                            f'FROM {self.db_table})')

        last = self.cursor.fetchall()
        if last == [entry]:
            print(f"Entry added successfuly to '{self.db_table}' "
                  f"from '{self.db_name}'")
        else:
            print('Error, something went wrong while adding the '
                  'entry to the table')

    @generic_connection(show_only_dbs=False)
    def remove_entry_from_db_tab(self):
        def get_int_rowid(rowid):
            try:
                rowid = int(rowid)
                if rowid not in self.df.index.tolist():
                    print('Number must be within the index range!')
                    return False
                return rowid
            except ValueError:
                print('Must be a number!')
                return False

        self.df_from_db_tab()
        print(f'{ffmt.bold}{fcol.green}{self.db_table.capitalize()} from '
              f'{self.db_name.capitalize()}:{ffmt.reset}\n{self.df_output}')

        while True:
            rowid = input('\nPick row id to remove or several '
                          '(e.g.: 3+6+1+34): ')
            if rowid == 'q':
                print('Aborted...')
                return
            elif '+' in rowid:
                rowid = rowid.split('+')
                rowid = [get_int_rowid(r) for r in rowid]
                if False not in rowid:
                    break
            else:
                rowid = get_int_rowid(rowid)
                if rowid is not False:
                    break

        self.df = self.df.drop(self.df.index[rowid])
        self.cursor.execute(f'DROP TABLE {self.db_table}')
        self.df.to_sql(self.db_table, self.db_con, index=False)
        self.refresh_dbs()

        db_tables_list = [x[1] for x in self.tabs_opts.values()
                          if x[0] == self.db_path]

        if self.db_table in db_tables_list:
            print("Entry removed!")
        else:
            print('Error, something went wrong replacing the table')

    @generic_connection(show_only_dbs=False)
    def db_tab_to_csv(self):
        self.df_from_db_tab()
        csv_out = oupt.files(question='Enter the directory for the csv file: ',
                             extension='csv', output_name=self.db_table)
        if csv_out == 'q':
            print('Aborted...')
            return

        self.df.to_csv(str(csv_out), encoding='utf-8', index=False)
        if os.path.exists(csv_out):
            print(f"Export done successfuly\nOutput at '{csv_out}'")
        else:
            print('Error, something went wrong exporting table to CSV')

    @generic_connection(show_only_dbs=True)
    def csv_to_db_tab(self):
        db_tables_list = [x[1] for x in self.tabs_opts.values()
                          if x[0] == self.db_path]
        csv_in_path = inpt.files(question='Enter the CSV file to import: ',
                                 extensions='csv')
        if csv_in_path == 'q':
            print('Aborted...')
            return

        csv_in_name = os.path.basename(str(csv_in_path))
        new_db_table_name = os.path.splitext(csv_in_name)[0]
        while True:
            ans = input(f"Enter the name for the table, or leave empty to "
                        f"name it '{new_db_table_name}': ")
            if ans == 'q':
                print('Aborted...')
                return
            elif ans == '':
                break
            elif len(ans) < 30 and ' ' not in ans:
                if ans in db_tables_list:
                    print(f"There is already a table named '{ans}'")
                    continue
                else:
                    new_db_table_name = ans
                    break
            print('Invalid name, might be too big')

        self.df = pd.read_csv(str(csv_in_path), delimiter=',')
        self.df.to_sql(new_db_table_name, self.db_con, index=False)
        db_name = os.path.basename(self.db_path)
        self.refresh_dbs()
        db_tables_list = [x[1] for x in self.tabs_opts.values()
                          if x[0] == self.db_path]

        if new_db_table_name in db_tables_list:
            print(f"Import done successfuly\nTable '{new_db_table_name}' "
                  f"created on '{db_name}'")
        else:
            print('Error, something went wrong creating the table from CSV')

    @generic_connection(show_only_dbs=True)
    def create_db_tab(self):
        db_tables_list = [x[1] for x in self.tabs_opts.values()
                          if x[0] == self.db_path]
        while True:
            db_table = input("Enter the name for the table: ")
            if db_table == 'q':
                print('Aborted...')
                return
            elif len(db_table) < 30 and ' ' not in db_table:
                if db_table in db_tables_list:
                    print(f"There is already a table named '{db_table}'")
                    continue
                else:
                    break
            print('Invalid name, might be too big or has spaces')

        columns = ''
        columns_name_list = []
        columns_type_opts = {'0': 'NULL',
                             '1': 'TEXT',
                             '2': 'INTEGER',
                             '3': 'REAL',
                             '4': 'BLOB'}
        while True:
            column_name = input('Enter the name for a column, or leave empty '
                                'to create the table: ')
            if column_name == 'q':
                print('Aborted...')
                return
            elif column_name == '':
                if len(columns_name_list) == 0:
                    print('Cannot create a table without any column')
                    continue
                break
            elif column_name in columns_name_list:
                print("'{column_name}' is already on the list")
                continue
            elif len(column_name) > 30 or ' ' in column_name:
                print('Invalid name for a column, '
                      'might be too big or as spaces')
                continue
            else:
                columns_type_opts_question = \
                    '\n'.join(sorted(
                        {f'[{x}] {y}'
                         for x, y in columns_type_opts.items()})) \
                    + f"\nChoose the data_type for '{column_name}': "
                column_type = qst.opts(question=columns_type_opts_question,
                                       opts_dict=columns_type_opts)
                if column_type == 'q':
                    print('Aborted...')
                    return
                columns_name_list.append((column_name, column_type))

        columns = ', '.join(f'{x[0]} {x[1]}' for x in columns_name_list)
        self.cursor.execute(f'CREATE TABLE {db_table} ({columns})')
        self.db_con.commit()
        self.refresh_dbs()
        db_tables_list = [x[1] for x in self.tabs_opts.values()
                          if x[0] == self.db_path]

        if db_table in db_tables_list:
            print(f"Table '{db_table}' created on '{self.db_name}'")
        else:
            print('Error, something went wrong creating the table')

    @generic_connection(show_only_dbs=False)
    def remove_db_tab(self):
        if input(f"Are you sure you want to remove '{self.db_table}' "
                 f"from '{self.db_name}' (y/N): ") == 'y':
            self.cursor.execute(f'DROP TABLE {self.db_table}')
            self.refresh_dbs()
            db_tables_list = [x[1] for x in self.tabs_opts.values()
                              if x[0] == self.db_path]
            if self.db_table not in db_tables_list:
                print('Table removed!')
            else:
                print('Error, something went wrong while removing the table')

    def create_db(self):
        self.refresh_dbs()
        while True:
            new_db = input('Enter the name for the new database: ')
            if new_db == 'q':
                print('Aborted...')
                return
            elif '/' in new_db or ' ' in new_db or len(new_db) > 30:
                print('Invalid name for a database')
                continue
            if not new_db.endswith('.db'):
                new_db += '.db'
            new_db_path = os.path.join(self.databases_path, new_db)
            if new_db_path in self.dbs_opts.values():
                print(f'{new_db} already exists')
                continue
            break

        subprocess.run(['touch', new_db_path])
        if os.path.exists(new_db_path):
            print(f"Database created successfuly at '{new_db_path}'")
        else:
            print('Error, something went wrong while creating the database')

    @generic_connection(show_only_dbs=True)
    def remove_db(self):
        if input(f"Are you sure you want to remove "
                 f"'{self.db_name}' (y/N): ") == 'y':
            os.remove(self.db_path)
            if not os.path.exists(self.db_path):
                print('Database removed!')
            else:
                print('Error, something went wrong '
                      'while removing the database')


db = Databases()
title = 'Databases-Menu'
keys = {'ls': (db.show_db_tab,
               "show database table"),
        'ad': (db.add_entry_to_db_tab,
               "add entry to a database table"),
        'rm': (db.remove_entry_from_db_tab,
               "remove entry from database table"),
        'dc': (db.db_tab_to_csv,
               "export database table to csv"),
        'cd': (db.csv_to_db_tab,
               "import database table from csv"),
        'adt': (db.create_db_tab,
                "create new database table"),
        'rmt': (db.remove_db_tab,
                "remove database table"),
        'add': (db.create_db,
                "create new database"),
        'rmd': (db.remove_db,
                "remove database")}
gmenu(title, keys)
