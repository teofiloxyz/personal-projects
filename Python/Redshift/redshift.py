#!/usr/bin/python3
"""Redshift gradual que deve ser executado a cada minuto (e.g.: systemd)
Também é possível tornar a main function num loop,
e correr o script como daemon (e.g.: $ setsid ...)"""

import time
import subprocess


RS_MAX_VAL, RS_MIN_VAL = 8500, 1250
RESET_LIGHT_HOUR, START_DECREASE_HOUR, STOP_DECREASE_HOUR = 6, 12, 23


class Redshift:
    def __init__(self) -> None:
        self.current_hour, self.current_minute = map(
            int, time.strftime("%H %M").split()
        )

    def main(self) -> None:
        if RESET_LIGHT_HOUR <= self.current_hour < START_DECREASE_HOUR:
            self.run_redshift(RS_MAX_VAL)
        elif (
            STOP_DECREASE_HOUR <= self.current_hour
            or RESET_LIGHT_HOUR > self.current_hour
        ):
            self.run_redshift(RS_MIN_VAL)
        else:
            self.run_redshift(rs_val=self.calculate_rs_val())

    def calculate_rs_val(self) -> int:
        """Baseado numa função afim (y = -ax + b), onde x é o tempo decorrido
        após a hora inicial, e y é o valor a atribuir ao redshift."""

        func_coef = (RS_MAX_VAL - RS_MIN_VAL) / (
            (STOP_DECREASE_HOUR - START_DECREASE_HOUR) * 60
        )
        minutes_since_hour_start = (
            self.current_hour - START_DECREASE_HOUR
        ) * 60 + self.current_minute
        return int(-func_coef * minutes_since_hour_start + RS_MAX_VAL)

    def run_redshift(self, rs_val: int) -> None:
        subprocess.run(["redshift", "-P", "-O", str(rs_val)])


if __name__ == "__main__":
    Redshift().main()
