#!/usr/bin/python3

import sys
import subprocess
from datetime import datetime, timedelta
from Tfuncs import gmenu, qst, rofi


class Calendars:
    def get_title(self, title=None, use_rofi=False):
        message = ""
        while True:
            if title is None:
                qst = "Who's the lucky person to have its birthday noted" \
                    if self.event == 'birthday' else \
                    'Enter the descriptive title for the event'
                if use_rofi:
                    self.title = rofi.simple_prompt(qst, message)
                else:
                    self.title = input(qst + ": ")
            else:
                self.title = title
                title = None

            if self.title == 'q':
                return False
            elif 0 < len(self.title) <= 30:
                break
            else:
                message = 'Title is too large, try another'
                print(message)

        if self.event == 'birthday':
            self.title = 'Aniversário: ' + self.title

    def get_date(self, use_rofi=False):
        if self.event == 'birthday':
            question = 'Enter the date for the birthday (e.g.: 20-2; 3 = 3-' \
                       'curr.month): '
        else:
            question = 'Enter the date for the event (e.g.: 28-8-21; 28 = ' \
                       '28-curr.M-curr.Y): '

        self.date = qst.get_date(question, date_type="%d/%m/%Y",
                                 use_rofi=use_rofi)
        if self.date == 'q':
            return False

    def get_hour(self, time, use_rofi=False):
        if time == 'beggining':
            question = 'Enter the hour of the event (e.g.: 9-35; ' \
                       '9 = 9-00) or leave empty for all day: '
        else:
            question = 'Enter the hour for the end of the event (e.g.: ' \
                       '18-23; 18 = 18-00) or leave empty for none: '

        self.hour = qst.get_hour(question, hour_type="%H:%M",
                                 use_rofi=use_rofi)
        if self.hour == 'q':
            return False

    @staticmethod
    def show_events(calendar, weeks):
        try:
            if int(weeks) < 1:
                print('Invalid number of weeks...')
                return
        except ValueError:
            print('Weeks must be a number...')
            return

        today = datetime.now().strftime('%d/%m/%Y')
        today_strp = datetime.strptime(today, '%d/%m/%Y')

        end_date_strp = (today_strp + timedelta(days=int(weeks)*7))
        end_date = end_date_strp.strftime('%d/%m/%Y')

        cmd = f'khal list {today} {end_date}' if calendar == 'all' else \
              f'khal list -a {calendar} {today} {end_date}'
        subprocess.run(cmd, shell=True)

    def personal_event(self, title=None, use_rofi=False):
        self.event = 'personal'

        if self.get_title(title, use_rofi=use_rofi) is False:
            print('Aborted...')
            return

        if self.get_date(use_rofi=use_rofi) is False:
            print('Aborted...')
            return

        if self.get_hour('beginning', use_rofi=use_rofi) is False:
            print('Aborted...')
            return

        alarm_msg = '[1] at the beginning of the event\n[2] 3h ' \
                    'before\n[3] 6h before\n[4] 1 day before\n' \
                    '[5] 3 days before\n[6] 7 days before\n[7] 14 days ' \
                    'before\n[8] 21 days'
        alarm_qst = 'Enter the alarms (e.g.: 2+5+1), ' \
                    'or leave empty for none'
        alarm_opts = {'1': '0m',
                      '2': '3h',
                      '3': '6h',
                      '4': '1d',
                      '5': '3d',
                      '6': '7d',
                      '7': '14d',
                      '8': '21d'}
        print(alarm_msg)
        message = alarm_msg
        while True:
            if use_rofi:
                alarm = rofi.simple_prompt(alarm_qst, message)
            else:
                alarm = input(alarm_qst + ": ")
            if alarm == 'q':
                print('Aborted...')
                return
            elif alarm == '':
                break

            if alarm in alarm_opts.keys():
                alarm = '--alarms ' + alarm_opts[alarm]
                break
            else:
                if '+' in alarm:
                    alarms_list = alarm.split('+')
                    alarm = '--alarms ' + ','.join([alarm_opts[alarm]
                                                    for alarm in alarms_list])
                    break
                message = 'Invalid answer...'
                print(message)

        description, category, special_options = '', '', False
        question = "Do you want any special option (Description or end-hour)?"
        if use_rofi:
            dmenu = ["No", "Yes"]
            ans = rofi.custom_dmenu(question, dmenu)
            if ans == "Yes":
                special_options = True
        else:
            if input(f':: {question} [y/N] ') == 'y':
                special_options = True

        if special_options:
            question = 'Enter the description for the event, ' \
                'or leave empty for none'
            if use_rofi:
                description = rofi.simple_prompt(question)
            else:
                description = input(question + ": ")
            if description == 'q':
                print('Aborted...')
                return
            description = \
                ':: "' + description + '"' if description != '' else ''

            if self.hour != '':
                # Muda a variável pq a função self.get_hour dá self.hour
                hour_begin = self.hour
                self.get_hour('end', use_rofi=use_rofi)
                if self.hour == 'q':
                    print('Aborted...')
                    return
                self.hour = hour_begin + '-' + self.hour \
                    if self.hour != '' else hour_begin

        cmd = f'khal new -a personal {self.date} {self.hour} "{self.title}" ' \
              f'{description} {category} {alarm}'
        exec_cmd = subprocess.call(cmd, shell=True)
        if exec_cmd == 0:
            msg = 'Calendar event added successfuly!'
        else:
            msg = 'Error adding the calendar event...'

        if use_rofi:
            rofi.message(msg)
        else:
            print(msg)

    def recurrent_event(self):
        self.event = 'recurrent'

        if self.get_title() is False:
            print('Aborted...')
            return

        if self.get_date() is False:
            print('Aborted...')
            return

        recurrence_qst = '[1]: yearly\n[2]: monthly\n[3]: weekly\n[4]: ' \
                         'daily\nEnter the recurrence: '
        recurrence_opts = {'1': '-r yearly',
                           '2': '-r monthly',
                           '3': '-r weekly',
                           '4': '-r daily'}
        recurrence = qst.opts(question=recurrence_qst,
                              opts_dict=recurrence_opts)
        if recurrence == 'q':
            print('Aborted...')
            return

        description = ''

        cmd = f'khal new -a recurrent {self.date} "{self.title}" ' \
              f'{description} {recurrence} --alarms -12h'
        exec_cmd = subprocess.call(cmd, shell=True)
        if exec_cmd == 0:
            print('Calendar event added successfuly!')
            print(f'Alarm at 12:00 on {self.date}')
        else:
            print('Error adding the calendar event...')

    def birthday_event(self):
        self.event = 'birthday'

        if self.get_title() is False:
            print('Aborted...')
            return

        if self.get_date() is False:
            print('Aborted...')
            return

        description = input('Enter a description for this person, '
                            'or leave empty for none: ')
        if description == 'q':
            print('Aborted...')
            return
        description = ':: "' + description + '"' if description != '' else ''

        cmd = f'khal new -a birthdays {self.date} "{self.title}" ' \
              f'{description} -r yearly --alarms -12h'
        exec_cmd = subprocess.call(cmd, shell=True)
        if exec_cmd == 0:
            print('Calendar event added successfuly!')
            print(f'Alarm at 12:00 on {self.date}')
        else:
            print('Error adding the calendar event...')

    @staticmethod
    def edit_event(calendar):
        if calendar == 'birthdays':
            question = 'Enter the name or aproximate name of the person to ' \
                       'edit, or <q> to quit: '
        else:
            question = 'Enter the title or aproximate title of the event to ' \
                        'edit, or <q> to quit: '

        title = input(question)
        if title == 'q':
            print("Aborting...\nTry the 'ls' option to have an ideia of the "
                  "event title")
            return

        subprocess.run(['khal', 'edit', '-a', calendar, title])


if __name__ == '__main__':
    if len(sys.argv) > 2:
        title = ' '.join(sys.argv[2:])
        if sys.argv[1] == 'create_personal_event':
            Calendars().personal_event(title, use_rofi=True)
        else:
            print('Argument error...')
    else:
        cal = Calendars()
        title = 'Calendars-Menu'
        keys = {'ls': (lambda weeks='2', calendar='all':
                       cal.show_events(calendar, weeks),
                       'show ALL events for the next two weeks',
                       '<# of weeks>: show ALL events for the next # weeks'),
                'lsp': (lambda weeks='2', calendar='personal':
                        cal.show_events(calendar, weeks),
                        'show personal events for the next two weeks',
                        '<# of weeks>: show personal events for the '
                        'next # weeks'),
                'lsr': (lambda weeks='2', calendar='recurrent':
                        cal.show_events(calendar, weeks),
                        'show recurrent events for the next two weeks',
                        '<# of weeks>: show recurrent events for the '
                        'next weeks'),
                'lsb': (lambda: cal.show_events(calendar='birthdays',
                                                weeks='53'),
                        'show all birthdays throughout the year'),
                'ad': (cal.personal_event,
                       "add new event to 'personal'"),
                'adr': (cal.recurrent_event,
                        "add new event to 'recurrent'"),
                'adb': (cal.birthday_event,
                        "add new event to 'birthdays'"),
                'ed': (lambda: cal.edit_event(calendar='personal'),
                       "edit/remove event from 'personal'"),
                'edr': (lambda: cal.edit_event(calendar='recurrent'),
                        "edit/remove event from 'recurrent'"),
                'edb': (lambda: cal.edit_event(calendar='birthdays'),
                        "edit/remove event from 'birthdays'")}
        gmenu(title, keys)
