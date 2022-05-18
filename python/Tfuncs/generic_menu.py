#!/usr/bin/python3
# CLI menu genérico usado em diversos scripts

import random


def menu(title, keys, extra_func=None):
    from Tfuncs import ffmt, fcol
    fcol_rand_pool = (fcol.red,
                      fcol.green,
                      fcol.yellow,
                      fcol.blue,
                      fcol.magenta,
                      fcol.cyan,
                      fcol.bright_red,
                      fcol.bright_green,
                      fcol.bright_yellow,
                      fcol.bright_blue,
                      fcol.bright_magenta,
                      fcol.bright_cyan)
    border_format = ffmt.bold + random.choice(fcol_rand_pool)
    title_format = ffmt.bold + random.choice(fcol_rand_pool)
    misc_format = ffmt.bold + random.choice(fcol_rand_pool)
    promt_format = ffmt.bold + fcol.blue

    menu_board1 = '/\\_'
    menu_board2 = '\\/ '
    title = 'Bem-vindo ao ' + title
    board_reps = 35
    title_space = \
        int(round((board_reps * len(menu_board1) - len(title)) / 2, 0))

    help_dialog = ''
    for key, descriptions in keys.items():
        try:
            int(key)
            key = f'[{key}]'
        except ValueError:
            pass
        if len(descriptions) > 2:
            help_dialog += f'{key}: {descriptions[1]}\n'
            for description in descriptions[2:]:
                help_dialog += f'{key} {description}\n'
        else:
            help_dialog += f'{key}: {descriptions[1]}\n'
    help_dialog += 'q: quit'

    menu = border_format + (menu_board1 * board_reps)[:-1] + '\n' \
        + menu_board2 * board_reps + ffmt.reset + '\n' + ' ' * title_space \
        + title_format + title.upper() + ffmt.reset + '\n' + border_format  \
        + (menu_board1 * board_reps)[:-1] + '\n' + menu_board2 * board_reps \
        + ffmt.reset + '\n\n' + misc_format + 'OPTIONS:' + ffmt.reset + '\n' \
        + help_dialog
    print(menu)

    if extra_func is not None:
        print('')
        extra_func()

    while True:
        key = input(f'{promt_format}\nPick what to do: {ffmt.reset}')
        if key == 'q':
            print('Quiting...')
            break
        elif key in keys:
            keys[key][0]()
        elif key.replace(' ', '') != '':
            if key.split()[0] in keys:
                try:
                    keys[key.split()[0]][0](key.split()[1])
                except (TypeError, IndexError):
                    print(help_dialog)
            else:
                print(help_dialog)
        else:
            print(help_dialog)
