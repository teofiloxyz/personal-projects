#!/usr/bin/python3
'''Redshift gradual que deve ser executado a cada minuto (e.g.: systemd)
Também é possível tornar a main function num loop,
e correr o script como daemon (e.g.: $ setsid ...)'''

import subprocess
from datetime import datetime


class Redshift:
    def __init__(self):
        self.rs_max_value, self.rs_min_value = 8500, 1250
        self.hour_light_reset = 6
        self.hour_start_decrease = 12
        self.hour_stop_decrease = 23
        self.current_hour = int(datetime.now().strftime("%H"))

    def main(self):
        if self.hour_light_reset <= self.current_hour \
                < self.hour_start_decrease:
            self.rs_value = str(self.rs_max_value)
            self.run_redshift()
        elif self.hour_stop_decrease <= self.current_hour \
                or self.current_hour < self.hour_light_reset:
            self.rs_value = str(self.rs_min_value)
            self.run_redshift()
        else:
            self.create_function()
            self.get_redshift_value()
            self.run_redshift()

    def create_function(self):
        '''Baseado numa função afim (y = -ax + b), onde x é o tempo decorrido
        após a hora inicial, e y é o valor a atribuir ao redshift.'''
        rs_val_delta = int(self.rs_max_value) - int(self.rs_min_value)
        mins_delta = (int(self.hour_stop_decrease)
                      - int(self.hour_start_decrease)) * 60
        self.func_a = rs_val_delta / mins_delta

    def get_redshift_value(self):
        current_min = int(datetime.now().strftime("%M"))
        mins_since_hour_start = (self.current_hour
                                 - self.hour_start_decrease) * 60 + current_min
        self.rs_value = str(- self.func_a * mins_since_hour_start
                            + self.rs_max_value)

    def run_redshift(self):
        subprocess.run(['redshift', '-P', '-O', self.rs_value],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


Redshift().main()
