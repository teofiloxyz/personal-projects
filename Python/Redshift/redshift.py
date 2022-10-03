#!/usr/bin/python3
"""Redshift gradual que deve ser executado a cada minuto (e.g.: systemd)
Também é possível tornar a main function num loop,
e correr o script como daemon (e.g.: $ setsid ...)"""

import time
import subprocess


RS_MAX_VAL, RS_MIN_VAL = 8500, 1250
RESET_LIGHT_HOUR, START_DECREASE_HOUR, STOP_DECREASE_HOUR = 6, 12, 23
CURRENT_HOUR, CURRENT_MINUTE = map(int, time.strftime("%H %M").split())


def main() -> None:
    if RESET_LIGHT_HOUR <= CURRENT_HOUR < START_DECREASE_HOUR:
        run_redshift(RS_MAX_VAL)
    elif STOP_DECREASE_HOUR <= CURRENT_HOUR or RESET_LIGHT_HOUR > CURRENT_HOUR:
        run_redshift(RS_MIN_VAL)
    else:
        run_redshift(CalculateRSVal().main())


class CalculateRSVal:
    """Baseado numa função afim (y = -ax + b), onde x é o tempo decorrido
    após a hora inicial, e y é o valor a atribuir ao redshift."""

    def main(self) -> int:
        func_coef = self.get_func_coefficient()
        minutes_since_hour_start = self.get_minutes_since_hour_start()
        return self.run_func(func_coef, minutes_since_hour_start)

    @staticmethod
    def get_func_coefficient() -> float:
        rs_vals_delta = RS_MAX_VAL - RS_MIN_VAL
        minutes_delta = (STOP_DECREASE_HOUR - START_DECREASE_HOUR) * 60
        return rs_vals_delta / minutes_delta

    @staticmethod
    def get_minutes_since_hour_start() -> float:
        return (CURRENT_HOUR - START_DECREASE_HOUR) * 60 + CURRENT_MINUTE

    @staticmethod
    def run_func(func_coef, minutes_since_hour_start) -> int:
        return int(-func_coef * minutes_since_hour_start + RS_MAX_VAL)


def run_redshift(rs_val: int) -> None:
    cmd = ["redshift", "-P", "-O", str(rs_val)]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
