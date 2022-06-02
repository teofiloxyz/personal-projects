#!/usr/bin/python3
# Menu de notificações com diversas funções

import os
import sys
import pickle
from datetime import datetime
from configparser import ConfigParser
from Tfuncs import gmenu, ffmt, fcol, qst, rofi


class History:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.hist_path = self.config['HISTORY']['history_path']
        self.notif_hist_list = [(file.split('.')[0],
                                get_notif_list(os.path.join(r_d_f[0], file)))
                                for r_d_f in os.walk(self.hist_path)
                                for file in r_d_f[2]]
        self.now = datetime.now()
        self.today_date = self.now.strftime('%Y-%m-%d')

    def show_all(self):
        for day in sorted(self.notif_hist_list):
            if day[0] == self.today_date:
                print(ffmt.bold + fcol.green + '\nTODAY:' + ffmt.reset)
            else:
                print(ffmt.bold + fcol.green + '\n' + day[0]
                      + ':' + ffmt.reset)
            print(*(f'{notif["time"]} - {notif["message"]}'
                    for notif in day[1]), sep='\n')

    def show_filter_urg(self, urg_level):
        col = fcol.bright_white
        if urg_level == 'low':
            col = fcol.green
        elif urg_level == 'normal':
            col = fcol.yellow
        elif urg_level == 'critical':
            col = fcol.red
        print(f'Showing all{ffmt.bold}{col} '
              f'{urg_level} urgency {ffmt.reset} past notifications')

        for day in sorted(self.notif_hist_list):
            if day[0] == self.today_date:
                print(ffmt.bold + fcol.green + '\nTODAY:' + ffmt.reset)
            else:
                print(ffmt.bold + fcol.green + '\n' + day[0]
                      + ':' + ffmt.reset)
            notif_list = [f'{notif["time"]} - {notif["message"]}'
                          for notif in day[1] if notif['urgency'] == urg_level]
            if len(notif_list) == 0:
                print('None')
            else:
                print('\n'.join(notif_list))


class Scheduled:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.scheduled_path = self.config['ALARMS']['scheduled_path']

        if os.path.exists(self.scheduled_path):
            with open(self.scheduled_path, 'rb') as sa:
                self.calendar_alarms_last_update, self.alarms_list = \
                    pickle.load(sa)
                self.scheduled_alarms_exist = True
        else:
            self.scheduled_alarms_exist = False

    def show_scheduled_alarms(self, index=False):
        if not self.scheduled_alarms_exist:
            print('Cannot find the file!')
            return

            # reversed não muda a variável
        for alarm in reversed(self.alarms_list):
            if index is False:
                print(f"{alarm['date']} - {alarm['msg']}")
            else:
                print(f"[{self.alarms_list.index(alarm) + 1}] {alarm['date']} "
                      f"- {alarm['msg']}")

    def get_date(self, date=None, use_rofi=False):
        question = 'Enter the date for the alarm (e.g.: 12-1-21; 27 = ' \
            '27-curr.M-curr.Y)'
        if not use_rofi:
            question += ": "
        return qst.get_date(question, date_type="%Y-%m-%d",
                            answer=date, use_rofi=use_rofi)

    def get_hour(self, hour=None, use_rofi=False):
        question = 'Enter the hour of the event ' \
            '(e.g.: 9-35; 9 = 9-00)'
        if not use_rofi:
            question += ": "
        return qst.get_hour(question, hour_type="%H:%M",
                            answer=hour, use_rofi=use_rofi)

    def update_scheduled_alarms(self):
        with open(self.scheduled_path, 'wb') as sa:
            pickle.dump([self.calendar_alarms_last_update, self.alarms_list],
                        sa)

    def create_alarm(self, msg=None, date=None, hour=None, use_rofi=False):
        if msg is None:
            qst = 'Enter the message of the alarm'
            if use_rofi:
                new_alarm_msg = rofi.simple_prompt(qst)
            else:
                new_alarm_msg = input(qst + ": ")
        else:
            new_alarm_msg = msg
        if new_alarm_msg in ('', 'q'):
            print('Aborted...')
            return

        if not self.scheduled_alarms_exist:
            print('Cannot find the file!')
            return False

        new_alarm_date = self.get_date(date, use_rofi=use_rofi)
        if new_alarm_date in ('', 'q'):
            print('Aborted...')
            return False

        new_alarm_hour = self.get_hour(hour, use_rofi=use_rofi)
        if new_alarm_hour in ('', 'q'):
            print('Aborted...')
            return False

        new_alarm_date = new_alarm_date + ' ' + new_alarm_hour
        new_alarm_date_strp = datetime.strptime(new_alarm_date,
                                                '%Y-%m-%d %H:%M')
        new_alarm_entry = {'uid': '#N/A',
                           'date': new_alarm_date,
                           'msg': new_alarm_msg}

        if len(self.alarms_list) == 0:
            self.alarms_list.append(new_alarm_entry)
        else:
            for alarm in self.alarms_list:
                alarm_date = alarm['date']
                alarm_date_strp = datetime.strptime(str(alarm_date),
                                                    '%Y-%m-%d %H:%M')
                if new_alarm_date_strp <= alarm_date_strp:
                    self.alarms_list.insert(self.alarms_list.index(alarm),
                                            new_alarm_entry)
                    break
                elif new_alarm_date_strp > alarm_date_strp \
                        and alarm == self.alarms_list[-1]:
                    self.alarms_list.append(new_alarm_entry)
                    break

        msg = f"New alarm '{new_alarm_msg}' on {new_alarm_date} added!"
        if use_rofi:
            rofi.message(msg)
        else:
            print(msg)
        self.update_scheduled_alarms()

    def remove_alarm(self):
        self.show_scheduled_alarms(index=True)

        while True:
            alarm_index = input('\nChoose the alarm to remove: ')
            if alarm_index == 'q':
                print('Aborted...')
                return

            try:
                alarm_index = int(alarm_index) - 1
                self.alarms_list.pop(alarm_index)
                self.update_scheduled_alarms()
                print('Alarm removed!')
                break
            except (ValueError, IndexError):
                print('Invalid answer...')


def get_notif_list(pkl_path):
    with open(pkl_path, 'rb') as pkl:
        notif_list = pickle.load(pkl)
        notif_list.reverse()
        return notif_list


def show_new_notif():
    config = ConfigParser()
    config.read('config.ini')
    new_notif_path = config['HISTORY']['new_path']
    if not os.path.exists(new_notif_path):
        print('No new notifications...')
        return

    print(f'{ffmt.bold}{fcol.red}NEW:{ffmt.reset}')
    notif_list = get_notif_list(new_notif_path)

    print(*(f'{notif["time"]} - {notif["message"]}'
            for notif in notif_list), sep='\n')
    os.remove(new_notif_path)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        msg = ' '.join(sys.argv[2:])
        if sys.argv[1] == 'create_notif':
            Scheduled().create_alarm(msg, use_rofi=True)
        else:
            print('Argument error...')
    else:
        hist = History()
        schd = Scheduled()
        title = 'Notifications-Menu'
        keys = {'ls': (hist.show_all,
                       "show all past notifications"),
                'lsl': (lambda: hist.show_filter_urg('low'),
                        "show all low urgency past notifications"),
                'lsn': (lambda: hist.show_filter_urg('normal'),
                        "show all normal urgency past notifications"),
                'lsc': (lambda: hist.show_filter_urg('critical'),
                        "show all critical urgency past notifications"),
                'lsa': (schd.show_scheduled_alarms,
                        "show all scheduled alarms for the next year"),
                'ad': (schd.create_alarm,
                       "create a notification alarm"),
                'rm': (schd.remove_alarm,
                       "remove a scheduled notification alarm")}
        extra_func = show_new_notif
        gmenu(title, keys, extra_func)
